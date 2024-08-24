# About

An app focused on RAG for Q+A and sourcing from markdown files.

## Tools
- HTMX + UI kit
- Python Server
- Python RAG
- Docker
- AWS Lightsail

## Components
- Rag lib for websocket streaming
- FastAPI backend
- HTMX + UIkit frontend
- User Chat Page
- Admin RAG Page

### Run the app
from root:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Testing
Spin up postgres db locally (see pal_infra repo)  
Connect through PGAdmin container if needed as well  

pytest - from root:
```bash
python -m pytest
```

### Code formatting
from root:
```bash
python -m black app
python -m black llm_lib
```

