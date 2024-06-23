from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Optional

from app.utils.auth import AuthCookie, get_auth_cookie
from app.utils.sessions import (
    get_session_id, 
    create_session, 
    create_user, 
    get_session_id, 
    get_user_from_session_id,
    get_user_admin
)

from app.config import TEMPLATES, TEMPLATES_SIMPLE_ENV

from pal import delete_index, get_available_files


router = APIRouter(tags=["admin"])

#templates = Jinja2Templates(directory="app/templates/admin")
index_files_template = TEMPLATES_SIMPLE_ENV.get_template("admin/responses/index_content_list.html")


@router.get(
  path="/admin",
  summary="Redirects to the login or reminders pages",
  tags=["Pages"],
  response_class=HTMLResponse
)
async def read_root(
  request:Request,
):
    session_id = get_session_id(request)

    if not session_id:
        session_id = create_session(request)
        user = create_user(request)
        path = '/admin/login'
        print("created session", session_id)
        print("created user", user)


    else:
        user_is_admin = get_user_admin(session_id)
    
        if user_is_admin:
            path = '/admin/home'
        else:
            path = '/admin/login'


    response = RedirectResponse(path, status_code=302)
    response.set_cookie(key="session_id", value=str(session_id))

    return response

@router.get(
  path="/admin/home",
  summary="Redirects to the login or reminders pages",
  tags=["Pages"],
  response_class=HTMLResponse
)
async def serve_admin_home(request: Request):
    context = {"request": request, "title": "Admin Home"}
    return TEMPLATES.TemplateResponse("admin/base.html", context)


@router.post("/upload")
async def upload_file():
    return {"message": "Upload File"}


@router.get("/file/{file_id}")
async def get_file(file_id: int):
    return {"file_id": file_id}


@router.get("/admin/files",
            response_class=HTMLResponse,
            tags=["Files"],
            summary="Get current documents"
        )
async def get_files(request:Request):
    files = get_available_files()
    index_list = index_files_template.render(files=files)
    return index_list


@router.get("/clear_index", response_class=HTMLResponse)
async def clear_index():
    delete_status = delete_index()
    return """<div id="index_content"> Index Cleared </div></br>"""