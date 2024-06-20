from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .chat_utils import handle_websocket_chat


router = APIRouter(prefix="/chat", tags=["chat"])


session_state = {}

# Initialize chat history
if "messages" not in session_state:
    session_state["messages"] = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await handle_websocket_chat(websocket, session_state)


@router.get("/clear_chat", response_class=HTMLResponse)
async def clear_chat():
    session_state["messages"] = []

    content_chunk = """<div id="content">
        <div id="history"></div>
        <div id="stream"></div>
        <div id="reference_data"></div>
        </div>"""

    return content_chunk


@router.websocket("/ws_for_testing")
async def websocket_endpoint(websocket: WebSocket):

    return await handle_websocket_chat(websocket)
