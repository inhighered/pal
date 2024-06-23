from fastapi import WebSocket, Request
from jinja2 import Environment, FileSystemLoader, PackageLoader
import markdown

from pal import open_ai_stream, create_and_query_vdb, create_and_retreive_context_vdb

import asyncio
from dataclasses import dataclass
from copy import deepcopy
from typing import Tuple, AsyncGenerator
import logging

from app.config import TEMPLATES, TEMPLATES_SIMPLE_ENV

logging.basicConfig(level=logging.DEBUG)

# Init templates to env
CHAT_TEMPLATES_PATH = "chat/responses"
stream_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_stream.html")
ref_data_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_ref_data.html")
history_template = TEMPLATES_SIMPLE_ENV.get_template(f"{CHAT_TEMPLATES_PATH}/chat_history.html")

logger = logging.getLogger(__name__)


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

    stream_generator = create_and_query_vdb(user_message).response_gen
    for stream_text in stream_generator:
        if stream_text is None:
            continue
        full_text += stream_text
        
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

    

async def handle_websocket_chat(websocket: WebSocket, session_state: dict):

    await websocket.accept()
    while True:
         
        # get the user message
        user_message = await websocket.receive_json()
        print(f"got data: {str(user_message)}")

        # update the state with the user message
        session_state["messages"].append({"role": "user", "content": user_message["chat_message"]})
        print("---------State after user message ---------------\n", session_state["messages"])

        # generate the chat history with all the messages
        chat_history = history_template.render(prev_messages=session_state["messages"])
        print("--------------chat history---------------: ", chat_history)

        # set stream as loading while waiting for the llm response 
        # (also fixes a an issue of old stream data still being rendered)
        await loading_user_response(websocket)

        # send the chat history to the user
        await websocket.send_text(chat_history)

        # set stream as loading while waiting for the llm response 
        # (also fixes a an issue of old stream data still being rendered)
        # await loading_user_response(websocket)

        # stream the llm response to the users message
        stream_html = await handle_websocket_stream(websocket, user_message["chat_message"])

        # update the system content state with the stream
        session_state["messages"].append({"role": "system", "content": stream_html})
        print("--------Current Messages--------- \n", session_state["messages"])

        # after streaming is done we need to put it in history - the old complete stream shouldn't show up as the new stream response
        stream_html = ""

        # finally return the ref info for the last message
        await return_chat_context(websocket, user_message["chat_message"])
        
