

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import uuid
import asyncio
from datetime import timedelta

from chat import handle_websocket_chat, ChatHistory

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --------------------------------------------------------------------------------
# Static Files
# --------------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

# we want to create these alongside a session
chat_history = ChatHistory()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    
    context = {
        "request": request,
        "title": "Streaming Chat"
    }

    response = templates.TemplateResponse("base.html", context)
    response.set_cookie(key="session_key", value=session_key, expires=timedelta(days=1))
    return response


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await handle_websocket_chat(websocket, chat_history)


@app.get("/clear_chat", response_class=HTMLResponse)
async def clear_chat():
    chat_history.clear_history()
    return """<div id="content" "hx-swap-oob=beforeend:#content"> chat cleared </div>"""
