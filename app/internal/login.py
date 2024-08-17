from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi import Request

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, PackageLoader
from typing import Optional
from typing_extensions import Annotated

#from app.utils.auth import AuthCookie, get_login_form_creds, get_auth_cookie
from app.utils.sessions import set_user_admin, get_user_admin
from app.config import TEMPLATES

router = APIRouter()


@router.get(
        path="/admin/login",
        summary="get login page",
        tags=["admin", "login"],
        response_class=HTMLResponse,
)
async def get_login(
        request: Request,
        invalid: Optional[bool] = None,
        logged_out: Optional[bool] = None,
        unauthorized: Optional[bool] = None,
    ) -> str:

    
    context = {'request': request, 
               'invalid': invalid,
               'logged_out': logged_out,
               'unauthorized': unauthorized}
    
    #login_resp = admin_login_template.render(**context)
    #login_resp = TEMPLATES.TemplateResponse("admin/base.html", context)
    login_resp = TEMPLATES.TemplateResponse("session/login.html", context)
    return login_resp

@router.post(
    path="/admin/login",
    summary="Log into app",
    tags = ["admin", "login"],
)
async def post_login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()], 
    request: Request,
) -> dict:
    print("logging in.....")

    session_id = request.cookies.get("session_id")

    if get_user_admin(session_id):
        return RedirectResponse(url="/admin/home", status_code=302)

    # hardcoded login for now
    if username == 'hayley' and password == 'hayley':
        response = RedirectResponse(url="/admin/home", status_code=302)
        # set session as admin session
        set_user_admin(session_id)
        return response
    else:

        response = RedirectResponse('/admin/login?invalid=True', status_code=302)
        return response
    # if cookie:
    #     response = RedirectResponse(url="/admin/home", status_code=302)
    #     response.set_cookie(key=cookie.name, value=cookie.token)
    #     print("setting cookie.....")
    # else:
    #     response = RedirectResponse('/admin/login?invalid=True', status_code=302)

    # return response


# logout = dict(
#   path="/admin/logout",
#   summary="Logs out of the app",
#   tags=["Authentication"]
# )
# @router.get(**logout)
# @router.post(**logout)
# async def admin_logout(
#     cookie: Optional[AuthCookie] = Depends(get_auth_cookie)
# ) -> dict:
#     if not cookie:
#         raise UnauthorizedException()
    
#     response = RedirectResponse(url="/admin/login?logged_out=True", status_code=302)
#     response.set_cookie(key=cookie.name, value=cookie.token, expires=-1)
#     return response