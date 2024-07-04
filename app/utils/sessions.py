from fastapi import Request
from fastapi.exceptions import HTTPException

from app.config import app_session, users
import random


# -----------------------------------------------
# Implement some basic session handling + auth
# -----------------------------------------------



def create_session(request:Request) -> int:
    # Session to user tracking
    # Create this if not exists
    for key in app_session.keys():
        if app_session[key]["user_ip"] == request.client.host:
            print("session already exists")
            session_id = app_session[key]["session_id"]
            return session_id

    else:
        session_id = len(app_session) + random.randint(0, 10000000)
        # request.client.host == users['user_ip']
        # like -- {"1293944": "10.01.20"}
        # Need to store if session is admin too
        # like { "1111111" : {"session_id": 11111111, "user_ip": "10.01.20", "is_admin": False}}
        session_info = {
            "session_id": session_id,
            "user_ip": request.client.host,
            "is_admin": False
        }

        app_session[session_id] = session_info

        return session_id


def create_user(request:Request) -> dict:
    # User ip tracking
    # Create user if not exists
    """
    User looks like:
    "10.01.20": {
        user_id: 1,
        user_ip: "10.01.20"
    }
    """

    user_ip = users.get(request.client.host)
    if user_ip:
        print("user already exists")
        return {"message": "User already exists"}

    else:
        new_user_id = len(users) + 1
        new_user_ip = request.client.host
        new_user = {
            "user_id": new_user_id,
            "user_ip": new_user_ip 
        }

        users[user_ip] = new_user

        return {"message": "User created successfully"}
    

def get_user_from_session_id(session_id: int):
    # returns none or user data

    user = None
    for user_data in users.values():
        session_user_ip = app_session[session_id]['user_ip']
        if user_data["user_ip"] == session_user_ip:
            user = user_data
            break
    return user


def get_session_id(request: Request) -> int:
    # just get the session id from the cookie, else none

    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in app_session:
        #raise HTTPException(status_code=401, detail="Invalid Session ID")
        return None
    return int(session_id)


def set_user_admin(session_id:int) -> dict:
    # set the user as an admin in the session (depend on login)
    app_session[int(session_id)]["is_admin"] = True
    return {"message": f"User {app_session[int(session_id)]['user_ip']} set to admin"}

def get_user_admin(session_id:int) -> bool:
    # get the user admin status from the session
    print("available sessions: ", app_session)
    print("session info:  ", app_session[int(session_id)])
    user_is_admin = app_session[int(session_id)]["is_admin"]
    return user_is_admin