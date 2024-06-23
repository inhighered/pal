# import jwt
# import secrets
# from typing import Optional
# from dataclasses import dataclass

# from fastapi import Cookie, Depends, Form
# from fastapi.security import HTTPBasic
# from app.utils.exceptions import UnauthorizedException
# from app.config import SECRET_KEY


# # -------------------------------------------
# # TODO - implement better auth later
# # -------------------------------------------

# # Globals
# basic_auth = HTTPBasic(auto_error=False)
# auth_cookie_name = "admin_session_key"

# @dataclass
# class AuthCookie:
#     name: str
#     token: str
#     username: str


# def _serialize_token(username: str) -> str:
#     return jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")

# def _deserialize_token(token: str) -> str:
#     try:
#         data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         return data['username']
#     except:
#         return None

# def get_login_form_creds(username: str = Form(), 
#                          password:str = Form()) -> Optional[AuthCookie]:
#     cookie = None

#     if not username == 'hayley':
#         print("not user hayley.....")
#         return None
    
#     print(f"Got----- username: {username}, password: {password}")
#     if secrets.compare_digest(password, username):
#         token = _serialize_token(username)
#         cookie = AuthCookie(
#             name = auth_cookie_name,
#             username=username,
#             token = token
#         )

#         return cookie


# def get_auth_cookie(admin_session: Optional[str] = Cookie(default =None)) -> Optional[AuthCookie]:
#     cookie = None
#     print("getting session cookie......")

#     if not admin_session:
#         print("not admin session.....")
#         return None

#     username = _deserialize_token(admin_session)

#     if not username == 'hayley':
#         print("not user hayley.....")
#         return None
    
#     cookie = AuthCookie(
#         name = auth_cookie_name,
#         username = username,
#         token=admin_session,
#     )



#     return cookie