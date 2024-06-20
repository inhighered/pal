from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import uuid
from datetime import timedelta

from .internal import admin
from .routers import chat

import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.include_router(chat.router)
app.include_router(admin.router)

# --------------------------------------------------------------------------------
# Static Files
# --------------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)

    context = {"request": request, "title": "Streaming Chat"}

    response = templates.TemplateResponse("base.html", context)
    response.set_cookie(key="session_key", value=session_key, expires=timedelta(days=1))
    return response
