from fastapi import WebSocket, APIRouter
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pal import delete_index


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
async def admin_home():
    return {"message": "Admin Home"}


@router.post("/upload")
async def upload_file():
    return {"message": "Upload File"}


@router.get("/file/{file_id}")
async def get_file(file_id: int):
    return {"file_id": file_id}


@router.get("/files")
async def get_files(file_id: int):
    return {"file_id": file_id}


@router.get("/clear_index", response_class=HTMLResponse)
async def clear_index():
    delete_status = delete_index()
    return """<div id="index_content"> Index Cleared </div></br>"""
