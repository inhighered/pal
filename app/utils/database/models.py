from dataclasses import dataclass, fields, field
from typing import List, Tuple
import datetime
import hashlib
from app.utils.database.db_utils import (
    with_connection,
    query, 
    query_no_cache,
    validate_types, 
    insert_with_conn
)

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
    chat_session: str # to track chat history, increment on clear
    chat_session_state: int # 1 - active, 0 - inactive
    message_type: str
    message: str
    doc_group_id: int # FK - Docs
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        validate_types(self)

    def insert(self):

        sql = """INSERT INTO
             app.chats (session_id, chat_session, chat_session_state, message_type, message, timestamp, doc_group_id)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)     
        """
        values = (
            self.session_id, 
            self.chat_session,
            self.chat_session_state,
            self.message_type, 
            self.message, 
            self.timestamp, 
            self.doc_group_id
        )
        _logger.debug(f"Inserting chat {self.session_id}, {self.chat_session}, {self.chat_session_state}, {self.message_type}, {self.message}, {self.timestamp}, {self.doc_group_id}, into app.chats")
        try:
            insert_with_conn(sql, values)
        except Exception as e:
            _logger.warning(f"Error {e} \nError inserting chat {self.session_id}, {self.chat_session}, {self.chat_session_state}, {self.message_type}, {self.message}, {self.timestamp}, {self.doc_group_id}, into app.chats")
            


@dataclass
class Doc:
    # PK auto generated (doc_id)
    doc_group_id: int # FK - Chat
    doc_name: str
    doc_location: str # we should either provide content or location
    doc_content: str # we should either provide content or location
    doc_active: int # 1 - active, 0 - inactive
    doc_hash: str = None

    def _hash_doc(doc:str) -> str:
        hash = hashlib.sha512(doc.encode()).hexdigest()
        return hash

    def __post_init__(self):
        doc_hash = self._hash_doc(self.doc_content)
        self.doc_hash = doc_hash
        validate_types(self)


    def insert(self):
        sql = """INSERT INTO
            app.docs (doc_group_id, doc_name, doc_location, doc_content, doc_hash, doc_active)
        VALUES
            (%s, %s, %s, %s, %s, %s)
        """
        values = (self.doc_group_id, self.doc_name, self.doc_location, self.doc_content, self.doc_hash, self.doc_active)
        _logger.debug(f"Inserting docs {self.doc_group_id}, {self.doc_name}, {self.doc_location}, {self.doc_content}, {self.doc_hash}, {self.doc_active} into app.docs")
        try:
            insert_with_conn(sql, values)
        except Exception as e:
            _logger.warning(f"Error {e} \nError inserting doc {self.doc_group_id}, {self.doc_location}, {self.doc_content}, {self.doc_hash}, {self.doc_active} into app.docs")
            

