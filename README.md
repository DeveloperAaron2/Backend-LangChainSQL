---
title: LangChain SQL Query API
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# LangChain SQL Query API

Backend API que permite consultar bases de datos SQLite usando lenguaje natural con LangChain y Google Gemini.

## Características

- 🔍 Conversión de preguntas en lenguaje natural a SQL
- 📊 Ejecución de queries y obtención de resultados estructurados
- 🤖 Generación de respuestas en lenguaje natural basadas en los resultados
- 🚀 API REST con FastAPI

## Endpoints

### `POST /get-sql-query`
Genera una query SQL a partir de una pregunta en lenguaje natural.

**Request:**
```json
{
  "query": "¿Cuáles son las 5 especies de árboles más comunes?"
}
```

**Response:**
```json
{
  "sql_query": "SELECT species, COUNT(*) as count FROM trees GROUP BY species ORDER BY count DESC LIMIT 5"
}
```

### `POST /get-sql-table`
Ejecuta una query SQL y devuelve resultados estructurados.

**Request:**
```json
{
  "query": "SELECT * FROM trees LIMIT 5"
}
```

**Response:**
```json
{
  "sql_table": {
    "columns": ["id", "species", "location"],
    "rows": [[1, "Oak", "Park A"], ...],
    "count": 5
  }
}
```

### `POST /get-answer`
Genera una respuesta en lenguaje natural a partir de los resultados.

**Request:**
```json
{
  "query": "¿Cuáles son los árboles más comunes?",
  "result": "{...resultados...}"
}
```

**Response:**
```json
{
  "human_answer": "Los árboles más comunes son..."
}
```

## Variables de Entorno

```bash
GOOGLE_API_KEY=tu_api_key_de_google_gemini
```

## Tecnologías

- FastAPI
- LangChain
- Google Gemini
- SQLAlchemy
- Python 3.11
