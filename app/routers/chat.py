from fastapi import WebSocket, APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routers.chat_utils import handle_websocket_chat
from app.utils.sessions import get_session_id

#router = APIRouter(prefix="/chat", tags=["chat"])
router = FastAPI()

# Your CORS
router.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO - Make this dependant on state
session_state = {}

# Initialize chat history
if "messages" not in session_state:
    session_state["messages"] = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await handle_websocket_chat(websocket, session_state)


@router.get("/clear_chat", response_class=HTMLResponse)
async def clear_chat(request: Request):

    
    session_id = get_session_id(request)
    print("Clearing chat history for session: ", session_id)
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
