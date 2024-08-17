from fastapi import APIRouter, Depends, UploadFile, Form, Response, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Optional, List

from app.utils.sessions import (
    get_session_id, 
    create_session, 
    create_user, 
    get_session_id, 
    get_user_from_session_id,
    get_user_admin,
    init_state,
)

from app.config import TEMPLATES, TEMPLATES_SIMPLE_ENV

from pal import (
    delete_index, 
    get_available_files, 
    clear_files, 
    get_index_exists_status,
    create_index_if_not_exists
)


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
        # session_id = create_session(request)
        # user = create_user(request)
        session_id = init_state(request)
        path = '/admin/login'
        print("created session", session_id)
        # print("created user", user)


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


@router.post("/admin/upload",
             response_class=HTMLResponse)
async def upload_file(response: Response,
                      file: UploadFile = File(...), 
                      ):

    # print("got files: ", files)

    contents = await file.read()

    print("got file: ",   file.filename)
    save_path = f"data/{file.filename}"
    with open(save_path, "wb+") as file_object:
        file_object.write(contents)

    response.headers['HX-Trigger'] = "fileUpdate"
    # save_file_local()

    content_chunk = """<div id="upload_status">
        </div>"""

    return content_chunk


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


@router.get("/admin/clear_index", response_class=HTMLResponse)
async def clear_index(response: Response):
    delete_status = delete_index()
    return """<div id="index_content"> Index Cleared </div></br>"""


@router.get("/admin/files/clear", response_class=HTMLResponse)
async def delete_files(response: Response):
    clear_status = clear_files()
    response.headers['HX-Trigger'] = "fileClear"
    return """<div></div>"""


@router.get("/admin/rebuild_index", response_class=HTMLResponse)
async def rebuild_index():

    _ = create_index_if_not_exists()
    return """<div id="index_rebuild"> Index Rebuilt or Index Already Exists </div></br>"""


@router.get("/admin/index_status", response_class=HTMLResponse)
async def index_status():
    status = get_index_exists_status()
    return f"""<div id="index_status"> Index Exists Status: {status} </div></br>"""


