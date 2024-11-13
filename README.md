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
deps - database
```bash
docker run --name pal-postgres-local -d --rm -v ${PWD}/local_volume:/var/lib/postgresql/data --env-file=db.env -p 5432:5432 pal-postgres
```

deps - ollama
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama run llama3.2:1b
```

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


#### Notes:
- Providing an OpenAI API Key is recommended. Open AI GPT 3.5 will be much better and still very cheap compared to a local ollama model.
- The "feature flag" for local llm vs open ai is bascially just the open ai key env var...