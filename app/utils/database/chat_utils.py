from typing import List

from app.utils.database.models import (
    Chat,
    User,
)

from app.utils.database.db_utils import (
    with_connection,
)

from psycopg import Connection

# ---------------- Chat Queries -----------------

@with_connection
def get_latest_chats(conn:Connection, user: User) -> List[Chat]:
    # get latest chat based on user ip
    # return false if no chat exists
    session_id = user.session_id
    sql = f"""SELECT 
        session_id,
        chat_session,
        chat_session_state,
        message_type,
        message,
        doc_group_id,
        timestamp
    FROM app.chats
        WHERE session_id = '{session_id}'
    ORDER BY timestamp DESC
    """

    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchall()

    chats = []
    for row in results_tuple:
        session_id, chat_session, chat_session_state, message_type, message, doc_group_id, timestamp  = row
        chat = Chat(session_id, chat_session, chat_session_state, message_type, message, doc_group_id, timestamp = timestamp)
        chats.append(chat)

    return chats


@with_connection
def clear_chat(conn:Connection, chat:Chat) -> bool:
    # clear chat history (soft delete) based on chat_session
    chat_session = chat.chat_session
    sql = f"""UPDATE
        chat_session_state = 0
    FROM app.chats
        WHERE chat_session = '{chat_session}'
    """
    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchone()
    response = results_tuple[0]
    return True
