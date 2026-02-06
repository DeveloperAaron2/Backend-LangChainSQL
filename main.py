import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchainApp import getSqlQuery, getSqlTable, getHumanAnswer, getColumns

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (suitable for public API)
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],  
    allow_headers=["*"],  
)


class QueryRequest(BaseModel):
    query: str

class AnswerRequest(BaseModel):
    query: str
    result: str

@app.post("/get-sql-query")
async def get_sql_query(request: QueryRequest):
    """
    Endpoint to generate SQL query from natural language question
    
    Args:
        request: QueryRequest with query field containing the natural language question
    
    Returns:
        dict with the generated SQL query
    """
    try:
        sql_query = getSqlQuery(request.query)
        return {
            "question": request.query,
            "sql_query": sql_query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-sql-table")
async def get_sql_table(request: QueryRequest):
    """
    Endpoint to get SQL table structure
    
    Args:
        request: QueryRequest with query field containing the natural language question
    
    Returns:
        dict with the SQL table structure
    """
    try:
        sql_table = getSqlTable(request.query)
        return {
            "sql_table": sql_table
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-answer")
async def get_answer(request: AnswerRequest):
    """
    Endpoint to get human answer from natural language question
    
    Args:
        request: QueryRequest with query field containing the natural language question
    
    Returns:
        dict with the human answer
    """
    try:
        human_answer = getHumanAnswer(request.query, request.result)
        return {
            "human_answer": human_answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/get-columns")
async def get_columns():
    try:
        columns = getColumns()
        return {
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"status": "success", "message": "API conectada a 0.0.0.0"}

if __name__ == "__main__":
    # HF Spaces y otros servicios usan PORT env variable
    # HF Spaces usa 7860 por defecto
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)