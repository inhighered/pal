from fastapi import WebSocket, Request
import markdown
import asyncio
from concurrent.futures import ThreadPoolExecutor

from pal import (
    create_and_query_vdb,
    create_and_retreive_context_vdb,
    create_index,
    manual_query,
    create_index_default_context,
    manual_get_query_context
)

from app.utils.test_generator import (
    response_generator, 
    rag_response_mock_generator, 
    mock_open_ai_response_generator
)

from app.utils.sessions import get_session_id

# db utils--
from app.utils.database.models import Chat, User
from app.utils.database.user_utils import get_user_from_ip
from app.utils.database.chat_utils import get_latest_chats, clear_chat
from app.utils.database.doc_utils import get_latest_doc_group



from openai import OpenAI

import asyncio
from dataclasses import dataclass
from copy import deepcopy
from typing import Tuple, AsyncGenerator, List
import logging

from app.config import TEMPLATES_SIMPLE_ENV


logging.basicConfig(level=logging.DEBUG)

client = OpenAI()

# Init templates to env
CHAT_TEMPLATES_PATH = "chat/responses"
stream_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_stream.html")
ref_data_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_ref_data.html")
history_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_history.html")

_logger = logging.getLogger(__name__)


async def loading_user_response(websocket: WebSocket) -> str:
    stream_loading_html = stream_template.render()
    await websocket.send_text(stream_loading_html)


async def response_generator_helper(user_message:str) -> AsyncGenerator[Tuple[str, str], None]:
    """
        Here we will create the vdb if it does not exist and query it
        The query will make use of RAG and the vdb.
        This also helps with response streaming.

    """

    full_text = ""

    # stream_generator = create_and_query_vdb(user_message).response_gen
    # query_engine, user_query = create_and_query_vdb(user_message)
    # stream_response = query_engine.query(user_query).response_gen
    stream_response = mock_open_ai_response_generator(user_message).response_gen

    # stream_response = manual_query(user_message).response_gen
    # stream_response = client.chat.completions.create(
    #         model='gpt-3.5-turbo',
    #         messages=[
    #             {'role': 'user', 'content': user_message}
    #         ],
    #         temperature=0,
    #         stream=True
    #         )
    
    for stream_text in stream_response:
        if stream_text is None:
            continue
        if stream_text.choices[0].delta.content:
            full_text += stream_text.choices[0].delta.content
        
        #full_text += stream_text
        
        stream_html = stream_template.render(current_stream = full_text)

        yield stream_html, full_text


async def handle_websocket_stream(websocket: WebSocket, user_message: str):

    async for stream_html, full_text in response_generator_helper(user_message):
        await websocket.send_text(stream_html)

    return full_text


async def return_chat_context(websocket: WebSocket, user_message:str):
    """
        Here we just get the context from the vdb and return it to the user
        We will either want to return the whole context, or just the context metadata.
        We don't worry about response streaming since the context/metadata doesn't require much processing.
    """

    reference_data = create_and_retreive_context_vdb(user_message, 
                                                     include_metadata=True,
                                                     include_content=False)
    reference_data = markdown.markdown(reference_data)
    print("reference_info--------------\n ", reference_data)

    ref_data_chunk = ref_data_template.render(reference_data=reference_data)
    await websocket.send_text(ref_data_chunk)

    return ref_data_chunk


async def async_index_wrapper(user_message) -> str:
    # To keep everything as async wrap the index stuff in a thread pool
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        index = await loop.run_in_executor(pool, create_index_default_context)

    with ThreadPoolExecutor() as pool:
        query = await loop.run_in_executor(pool, manual_get_query_context, index, user_message)

    return query
    


async def initialize_chat_history(session_ip: str)-> Tuple[User, List[Chat], int]:
    
    user = get_user_from_ip(session_ip)
    chats = get_latest_chats(user)
    doc_group_id = get_latest_doc_group()

    return user, chats, doc_group_id


async def handle_websocket_chat(websocket: WebSocket, session_state: dict):

    await websocket.accept()

    # ---Initialize chat history-----
    session_ip = websocket.client.host
    user, chats, doc_group_id = await initialize_chat_history(session_ip)

    if chats != []:
        for chat in chats:
            session_state["messages"].append({"role": chat.message_type, "content": chat.message})

    if chats != []:
        existing_chat_session = chats[0].chat_session
    else:
        existing_chat_session = '0'


    while True:

        # get the user message
        user_message = await websocket.receive_json()
        print(f"got data: {str(user_message)}")

        # update the state with the user message
        session_state["messages"].append({"role": "user", "content": user_message["chat_message"]})
        user_chat = Chat(
            user.session_id, # session_id
            existing_chat_session, # chat_session
            1, # chat_session_state: int # 1 - active, 0 - inactive
            "user", # message_type: str
            user_message["chat_message"], # message: str
            doc_group_id
        )

        user_chat.insert()

        print("---------State after user message ---------------\n", session_state["messages"])

        # generate the chat history with all the messages
        chat_history = history_template.render(prev_messages=session_state["messages"])
        print("--------------chat history---------------: ", chat_history)

        # set stream as loading while waiting for the llm response 
        # (also fixes a an issue of old stream data still being rendered)
        await loading_user_response(websocket)

        # send the chat history to the user
        await websocket.send_text(chat_history)

        # Handle creating the index + generating new context
        query = await async_index_wrapper(user_message["chat_message"])


        # after streaming is done we need to put it in history - the old complete stream shouldn't show up as the new stream response
        system_text = ""
        
        # stream the llm response to the users message
        # stream_html = await handle_websocket_stream(websocket, user_message["chat_message"])
        system_text = await handle_websocket_stream(websocket, query)

        # update the system content state with the stream
        session_state["messages"].append({"role": "system", "content": system_text})

        sys_chat = Chat(
            user.session_id, # session_id
            existing_chat_session, # chat_session
            1, # chat_session_state: int # 1 - active, 0 - inactive
            "system", # message_type: str
            system_text, # message: str
            doc_group_id
        )
        sys_chat.insert()

        print("--------Current Messages--------- \n", session_state["messages"])


        # finally return the ref info for the last message
        await return_chat_context(websocket, user_message["chat_message"])


        



def clear_session_chat(request:Request) -> None:
    session_ip = request.client.host
    _logger.info(f"Clearing chat history for session: {get_session_id(request)}")
    _logger.info(f"Clearing chat history for user ip: {session_ip}")
    user = get_user_from_ip(session_ip)
    chats = get_latest_chats(user)
    for chat in chats:
        clear_chat(chat)

    return None




## -----------------------------------
# ---------- Testing Funcs ------------
## -----------------------------------

# async def simple_response_generator_helper(user_message:str):
#     full_text = ""
#     stream_generator = response_generator(user_message)
#     for stream_text in stream_generator:
#         if stream_text is None:
#             continue
#         full_text += stream_text
        
#         stream_html = stream_template.render(current_stream = full_text)

#         yield stream_html


# async def simple_handle_websocket_stream(websocket: WebSocket, user_message: str):

    
#     async for stream_html in simple_response_generator_helper(user_message):
#         await websocket.send_text(stream_html)

#     return stream_html
    


# async def simple_ws_test(websocket: WebSocket):
#     session_state = {}

#     # Initialize chat history
#     if "messages" not in session_state:
#         session_state["messages"] = []


#     await websocket.accept()
#     while True:
        
        
#         user_message = await websocket.receive_json()
#         #print(f"got data: {str(user_message)}")
#         session_state["messages"].append({"role": "user", "content": user_message["chat_message"]})
#         chat_history = history_template.render(prev_messages=session_state["messages"])
#         #print(chat_history)
#         await websocket.send_text(chat_history)

#         stream_html = await simple_handle_websocket_stream(websocket, user_message["chat_message"])


#         session_state["messages"].append({"role": "system", "content": stream_html})
     



