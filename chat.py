
from fastapi import WebSocket
from jinja2 import Environment, FileSystemLoader
import markdown

from pal import open_ai_stream, create_and_query_vdb, create_and_retreive_context_vdb

import asyncio
from dataclasses import dataclass
from copy import deepcopy
from typing import Tuple, AsyncGenerator
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('templates'))
history_template = env.get_template("responses/chat_history.html")
stream_template = env.get_template("responses/chat_stream.html")
stream_loading_template = env.get_template("responses/chat_stream_loading.html")
ref_data_template = env.get_template("responses/chat_ref_data.html")




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
        

# after message 1
#  [{'role': 'user', 'content': 'What are HBs fun facts?'}, {'role': 'system', 'content': "HB's fun facts include her favorite things such as video games like Sims 4, Stardew Valley, and Civ 6, podcasts like Who? Weekly and Mostly Nitpicking, movies like Lord of the Rings and MCU films, and TV shows without commercials. She also has a dog named Gatsby and her partner, Preston, has a background in chemical engineering."}]
# after message 2 (before ref)
# State after user message 1
# [{'role': 'user', 'content': 'What are HBs fun facts?'}]
# State after user message 2
#  [{'role': 'user', 'content': 'What are HBs fun facts?'}, 
# {'role': 'system', 'content': "HB's fun facts include her favorite things such as video games like the Sims 4, quest-heavy open-worlds like Stardew Valley, and casual strategy sims like Civ 6. She enjoys podcasts on film/tv critics and pop culture conversations, with some of her top picks being Who? Weekly and Mostly Nitpicking. HB also loves movies, especially rewatching Lord of the Rings annually and having her top three MCU runs. Additionally, she enjoys TV shows without commercials and has a dog named Gatsby."}, 
# {'role': 'user', 'content': 'What materials do I need?'}]

# Chat history actually looks good too (no prev stream messages)
# stream html is also blank?

# so must be old stream data? or maybe actually a frontend artifact?

