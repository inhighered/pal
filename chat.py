
from fastapi import WebSocket
from jinja2 import Environment, FileSystemLoader

from src.llm.simple import open_ai_stream

import asyncio
from dataclasses import dataclass
from copy import deepcopy
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader('templates'))
chat_template = env.get_template("responses/chat.html")

# initial states
user_messages = "My Message"
message_history = "Chatbot Response"

@dataclass
class ChatHistory:
    history: dict = None
    last_message_id:int = None

    async def new_message(self, message_type:str, message:str) -> None:
        if self.history is None:
            self.history = {}
        if self.last_message_id is None:
            self.last_message_id = 0
        else:
            self.last_message_id += 1

        self.history.update({self.last_message_id: {"message_type": message_type, "message": message}})
    
    async def update_latest_message(self, message_type:str, message:str) -> None:
        if self.history is None:
            self.history = {}
        if self.last_message_id is None:
            self.last_message_id = 0

        self.history.update({self.last_message_id: {"message_type": message_type, "message": message}})

    async def previous_messages(self) -> dict:

        self.last_message_id

        prev_messages = {}
        for key, val in self.history.items():
            if key < self.last_message_id:
                await prev_messages.update({key: val})

        return prev_messages

    async def clear_history(self) -> None:
        self.history = None
        

# start a new chat history with the user session


async def chat_streamer(user_message:str, chat_history: ChatHistory):


    # chat_history = ChatHistory()
    sys_response = ""

    await chat_history.new_message("user", user_message)
    prev_messages = deepcopy(chat_history.history)
    await chat_history.new_message("system", sys_response)

    for i in range(3):

        # call llm (return generator)
        sys_response = " system message #"
        sys_response = sys_response + str(i)

        await chat_history.update_latest_message("system", sys_response)

        # Prob need form here

        await asyncio.sleep(0.1)

        print(prev_messages)
        context = {
        "prev_messages": prev_messages,
        "current_message": sys_response
        }

        chat = chat_template.render(**context)
        #print(chat)
        yield chat



async def chat_streamer_open_ai(user_message:str, chat_history: ChatHistory):

    # chat_history = ChatHistory()
    sys_response = ""

    await chat_history.new_message("user", user_message)
    prev_messages = deepcopy(chat_history.history)
    await chat_history.new_message("system", sys_response)

    stream = open_ai_stream(user_message)
    for chunk in stream:
        if chunk.choices[0].delta.content is None:
            continue

        # call llm (return generator)
        # sys_response = " system message #"
        # sys_response = sys_response + str(i)
        sys_response = sys_response + chunk.choices[0].delta.content


        await chat_history.update_latest_message("system", sys_response)

        #await asyncio.sleep(0.1)

        print(prev_messages)
        context = {
        "prev_messages": prev_messages,
        "current_message": sys_response
        }

        chat = chat_template.render(**context)
        print(chat)

        yield chat


async def chat_stream_renderer(websocket: WebSocket, user_messages, chat_history):
    async for my_text in chat_streamer_open_ai(user_messages, chat_history):
        await websocket.send_text(my_text)

async def handle_websocket_chat(websocket: WebSocket, chat_history: ChatHistory):

    await websocket.accept()
    while True:

        user_message = await websocket.receive_json()
        print(f"got data: {str(user_message)}")
        user_message = user_message["chat_message"]  

        await chat_stream_renderer(websocket, user_message, chat_history)
