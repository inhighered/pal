
from fastapi import WebSocket
from jinja2 import Environment, FileSystemLoader
import markdown

from pal import open_ai_stream, create_and_query_vdb, create_and_retreive_context_vdb

import asyncio
from dataclasses import dataclass
from copy import deepcopy
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('templates'))
history_template = env.get_template("responses/chat_history.html")
stream_template = env.get_template("responses/chat_stream.html")
ref_data_template = env.get_template("responses/chat_ref_data.html")


async def response_generator_helper(user_message:str):
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

        yield stream_html


async def handle_websocket_stream(websocket: WebSocket, user_message: str):

    async for stream_html in response_generator_helper(user_message):
        await websocket.send_text(stream_html)

    return stream_html


async def return_chat_context(websocket: WebSocket, user_message:str):
    """
        Here we just get the context from the vdb and return it to the user
        We will either want to return the whole context, or just the context metadata.
        We don't worry about response streaming since the context/metadata doesn't require much processing.
    """

    reference_data = create_and_retreive_context_vdb(user_message)
    reference_data = markdown.markdown(reference_data)
    print("reference_info--------------\n ", reference_data)

    ref_data_chunk = ref_data_template.render(reference_data=reference_data)
    await websocket.send_text(ref_data_chunk)

    return ref_data_chunk

    

async def handle_websocket_chat(websocket: WebSocket, session_state: dict):

    await websocket.accept()
    while True:
         
        user_message = await websocket.receive_json()
        #print(f"got data: {str(user_message)}")
        session_state["messages"].append({"role": "user", "content": user_message["chat_message"]})
        chat_history = history_template.render(prev_messages=session_state["messages"])

        await websocket.send_text(chat_history)
        stream_html = await handle_websocket_stream(websocket, user_message["chat_message"])

        session_state["messages"].append({"role": "system", "content": stream_html})

        await return_chat_context(websocket, user_message["chat_message"])
        