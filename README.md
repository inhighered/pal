# About

An app focused on RAG for Q+A and sourcing from markdown files.

# Prod
- llm python package
- Docker
- AWS


# Dev

### Run the app
from root:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing - pytest
from root:
```bash
python -m pytest
```

### Code formatting
from root:
```bash
python -m black app
python -m black llm_lib
```

