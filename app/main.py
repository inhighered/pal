from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import uuid
from datetime import timedelta

from .internal import admin, login
from .routers import chat
from app.config import TEMPLATES
from app.utils.sessions import  create_session, create_user

import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(admin.router)
app.include_router(login.router)
app.mount("/chat", chat.router)

# --------------------------------------------------------------------------------
# Static Files
# --------------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # basic session setup
    # session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    # response.set_cookie(key="session_key", value=session_key, expires=timedelta(days=1))

    # session with users:
    session_id = create_session(request)
    user_status = create_user(request)

    print("session id: ", session_id)
    print("user status: ", user_status)

    context = {"request": request, "title": "Streaming Chat"}
    response = TEMPLATES.TemplateResponse("base.html", context)

    response.set_cookie(key="session_id", value=str(session_id), expires=timedelta(days=1))
                            
    return response

