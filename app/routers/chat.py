from fastapi import WebSocket, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routers.chat_utils import handle_websocket_chat, clear_session_chat
from app.routers.mock_chat_utils import mock_handle_websocket_chat
from app.utils.sessions import get_session_id, get_session_id_ws

#router = APIRouter(prefix="/chat", tags=["chat"])
router = APIRouter()

# # # TODO - Make this dependant on state
# session_state = {}

# # Initialize chat history
# if "messages" not in session_state:
#     session_state["messages"] = []



@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):


    #return await handle_websocket_chat(websocket, session_state)
    return await handle_websocket_chat(websocket)
    # works
    # return await simple_ws_test(websocket)

    # returns user text + loading spinner, but no text is returned
    # return await mock_handle_websocket_chat(websocket, session_state)


@router.get("/chat/clear_chat", response_class=HTMLResponse)
async def clear_chat(request: Request):
    # I guess this should start a new chat group?

    session_id = get_session_id(request)
    print("Clearing chat history for session: ", session_id)
    # session_state["messages"] = []
    clear_session_chat(request)

    content_chunk = """<div id="content">
        <div id="history"></div>
        <div id="stream"></div>
        <div id="reference_data"></div>
        </div>"""

    return content_chunk




@router.websocket("/ws_for_testing")
async def websocket_endpoint(websocket: WebSocket):
    # this should return users ip:
    # websocket.client.host

    return await handle_websocket_chat(websocket)
    # return await mock_handle_websocket_chat(websocket, session_state)