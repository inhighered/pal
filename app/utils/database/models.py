from dataclasses import dataclass, fields, field
import datetime
from app.utils.database.db_utils import (
    with_connection,
    query, 
    query_no_cache,
    validate_types, 
    insert_with_conn
)

from psycopg import Connection

from logging import getLogger
_logger = getLogger(__name__)

@dataclass
class User:
    session_id: str # PK
    user_ip: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        validate_types(self)

    def insert(self):

        sql = """INSERT INTO 
            app.users (session_id, user_ip, timestamp)
        VALUES
            (%s, %s, %s)
        """
        _logger.debug(f"Inserting user {self.session_id}, {self.user_ip}, {self.timestamp} into app.users")
        values = (self.session_id, self.user_ip, self.timestamp)
        try:
            insert_with_conn(sql, values)
        except Exception as e:
            _logger.warning(f"Error {e} \nError inserting user {self.session_id}, {self.user_ip}, {self.timestamp} into app.users")

       
    def get_user_chats(self):
        sql = f"""SELECT 
            message_type, message, doc_group_id, timestamp
        FROM 
            app.chats
        WHERE 
            session_id = {self.session_id}
        """
        _logger.debug(f"Getting chats for user {self.session_id}")
        try:
            col_names, rows = query_no_cache(sql)
            chats = []
            for row in rows:
                message_type, message, doc_group_id, timestamp = row
                chat = Chat(self.session_id, message_type, message, doc_group_id, timestamp = timestamp)
                chats.append(chat)
        except Exception as e:
            _logger.warning(f"Error {e} \nError getting chats for user {self.session_id}")
            chats = None

        return chats
    


@dataclass
class Chat:
    # PK auto generated (chat_id)
    session_id: str # FK - Users
    message_type: str
    message: str
    doc_group_id: int # FK - Docs
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        validate_types(self)

    def insert(self):

        sql = """INSERT INTO
             app.chats (session_id, message_type, message, timestamp, doc_group_id)
        VALUES
            (%s, %s, %s, %s, %s)     
        """
        values = (
            self.session_id, 
            self.message_type, 
            self.message, 
            self.timestamp, 
            self.doc_group_id
        )
        _logger.debug(f"Inserting chat {self.session_id}, {self.message_type}, {self.message}, {self.timestamp}, {self.doc_group_id}, into app.chats")
        values = (self.session_id, self.user_ip, self.timestamp)
        try:
            insert_with_conn(sql, values)
        except Exception as e:
            _logger.warning(f"Error {e} \nError inserting chat {self.session_id}, {self.message_type}, {self.message}, {self.timestamp}, {self.doc_group_id}, into app.chats")
            

@dataclass
class Docs:
    # PK auto generated (doc_id)
    doc_group_id: int # FK - Chat
    doc_names: str

    def __post_init__(self):
        validate_types(self)

    def insert(self):
        sql = """INSERT INTO
            app.docs (doc_group_id, doc_names)
        VALUES
            (%s, %s)
        """
        values = (self.doc_group_id, self.doc_names)
        _logger.debug(f"Inserting docs {self.doc_group_id}, {self.doc_names} into app.docs")
        try:
            insert_with_conn(sql, values)
        except Exception as e:
            _logger.warning(f"Error {e} \nError inserting doc {self.doc_group_id}, {self.doc_names} into app.docs")
            


@with_connection
def get_latest_docs(conn:Connection):
    sql = """SELECT 
        doc_group_id
    FROM 
        app.docs
    ORDER BY doc_group_id DESC 
    LIMIT 1"""
    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchone()
    doc_group_id = results_tuple[0]
    return doc_group_id


@with_connection
def get_user_from_ip(conn: Connection, user_ip: str) -> User:
    sql = f"""SELECT 
        session_id,
        user_ip,
        timestamp
    FROM 
        app.users
    WHERE 
        user_ip = '{user_ip}'
    ORDER BY timestamp DESC 
    LIMIT 1
    """
    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchone()

    user = User(str(results_tuple[0]), str(results_tuple[1]), timestamp = results_tuple[2])
    
    return user
