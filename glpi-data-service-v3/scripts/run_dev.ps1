$env:POSTGRES_PORT="5433"
uvicorn src.main:app --reload --port 8001
