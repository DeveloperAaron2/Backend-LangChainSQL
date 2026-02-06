import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from langchain_google_genai import ChatGoogleGenerativeAI

google_api_key = os.environ["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(google_api_key=google_api_key, model="gemini-2.5-flash-lite")

from langchain_core.messages import HumanMessage

from langchain_community.utilities import SQLDatabase

sqlite_db_path = "data/car_dataset.sqlite"

db = SQLDatabase.from_uri(f"sqlite:///{sqlite_db_path}")

from langchain_classic.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, ListSQLDatabaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser




def getSqlQuery(question):
    chain = create_sql_query_chain(llm, db)
    response = chain.invoke({"question": question})
    return response

def getSqlTable(sql_query):
    """Execute SQL query and return structured results"""
    import ast
    import re
    
    try:
        # Use db.run() to execute the query and get results
        result_str = db.run(sql_query)
        
        # Try to parse the string representation of tuples
        if result_str.startswith('['):
            # Parse the string as Python literal (list of tuples)
            try:
                result_data = ast.literal_eval(result_str)
            except:
                return {"raw": result_str, "columns": [], "rows": []}
            
            if isinstance(result_data, list) and len(result_data) > 0:
                # Try to get column names from the query
                select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql_query, re.IGNORECASE | re.DOTALL)
                
                if select_match:
                    columns_part = select_match.group(1).strip()
                    if columns_part == '*':
                        # If SELECT *, use generic column names
                        num_cols = len(result_data[0]) if isinstance(result_data[0], tuple) else 1
                        columns = [f"Column_{i+1}" for i in range(num_cols)]
                    else:
                        # Parse column names from SELECT clause
                        # Handle aliases with AS keyword
                        col_parts = []
                        for col in columns_part.split(','):
                            col = col.strip()
                            # Check for AS alias
                            if ' AS ' in col.upper():
                                alias = col.upper().split(' AS ')[-1].strip()
                                col_parts.append(alias.lower())
                            else:
                                # Take the last part after dot (for table.column)
                                col_parts.append(col.split('.')[-1].strip())
                        columns = col_parts
                else:
                    # Fallback: generic column names
                    num_cols = len(result_data[0]) if isinstance(result_data[0], tuple) else 1
                    columns = [f"Column_{i+1}" for i in range(num_cols)]
                
                # Convert tuples to lists
                rows = [list(row) if isinstance(row, tuple) else [row] for row in result_data]
                
                return {
                    "columns": columns,
                    "rows": rows,
                    "count": len(rows)
                }
        
        # If we can't parse it, return raw result  
        return {"raw": result_str, "columns": [], "rows": []}
        
    except Exception as e:
        return {"error": str(e), "columns": [], "rows": []}


def getHumanAnswer(question, result):
    """Generate a natural language answer from query results"""
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question and SQL result, answer the user question in a natural way.

    Question: {question}
    SQL Result: {result}
    Answer: """
    )
    
    chain = answer_prompt | llm | StrOutputParser()
    response = chain.invoke({"question": question, "result": str(result)})
    return response



def getColumns():
    """Get top 10 rows from the table with all columns"""
    import ast
    
    try:
        tables = db.get_usable_table_names()
        if not tables:
            return {"error": "No tables found in database", "columns": [], "rows": []}
        
        table_name = tables[0] 
        
        query = f"SELECT * FROM {table_name} LIMIT 10"
        result_str = db.run(query)
        
        if result_str.startswith('['):
            try:
                result_data = ast.literal_eval(result_str)
            except:
                return {"raw": result_str, "columns": [], "rows": []}
            
            if isinstance(result_data, list) and len(result_data) > 0:
                # Get column names using PRAGMA table_info - most reliable method
                pragma_query = f"PRAGMA table_info({table_name})"
                pragma_result = db.run(pragma_query)
                
                # Parse PRAGMA result to get column names
                # PRAGMA returns: (cid, name, type, notnull, dflt_value, pk)
                try:
                    pragma_data = ast.literal_eval(pragma_result)
                    # Extract column names from position 1 of each tuple
                    columns = [col[1] for col in pragma_data]
                except:
                    # Fallback: use generic column names
                    num_cols = len(result_data[0]) if isinstance(result_data[0], tuple) else 1
                    columns = [f"Column_{i+1}" for i in range(num_cols)]
                
                rows = [list(row) if isinstance(row, tuple) else [row] for row in result_data]
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "rows": rows,
                    "count": len(rows)
                }
        
        return {"raw": result_str, "columns": [], "rows": []}
        
    except Exception as e:
        return {"error": str(e), "columns": [], "rows": []}

