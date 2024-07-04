import time
from typing import Generator, List, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass, field
import asyncio
from openai import OpenAI

client = OpenAI()

def response_generator(user_message: str):
    # In a real scenario we would want to pass the user message to an LLM
    response = "Hello there! How can I assist you today?" * int(100) # 10,000 characters

    for word in response.split():
        yield word + " "


TokenGen = Generator[str, None, None]
TokenAsyncGen = AsyncGenerator[str, None]

@dataclass
class StreamingResponse:
    response_gen: TokenGen
    source_nodes: List = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    response_txt: Optional[str] = None


@dataclass
class AsyncStreamingResponse:
    response_gen: TokenAsyncGen
    source_nodes: List = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    response_txt: Optional[str] = None

def mock_stream() -> Generator:
    response = "Hello there! How can I assist you today?" * int(100) # 10,000 characters

    for word in response.split():
        yield word + " "

async def async_mock_stream() -> AsyncGenerator:
    response = "Hello there! How can I assist you today?" * int(100) # 10,000 characters

    for word in response.split():
        # this will bind the generator
        # time.sleep(0.01)
        # asyncio.sleep(0.1) <- would need to be in async
        yield word + " "

def rag_response_mock_generator(user_message:str) -> StreamingResponse:
    """
        This function is a mock of the llamaindex chat function
        It will return a mock stream of responses from the vdb.
    """
    time.sleep(0.5)
    stream_resp = StreamingResponse(
        response_gen=mock_stream(),
        source_nodes=[],
        metadata = {},
        response_txt="streaming response mock"
    )

    return stream_resp

        
async def async_rag_response_mock_generator(user_message:str):
    """
        This function is a mock of the llamaindex chat function
        It will return a mock stream of responses from the vdb.
    """
    await asyncio.sleep(0.5)
    stream_resp = AsyncStreamingResponse(
        response_gen=async_mock_stream(),
        source_nodes=[],
        metadata = {},
        response_txt="streaming response mock"
    )

    return stream_resp


from openai import OpenAI
client = OpenAI()

def mock_open_ai_response_generator(user_message:str)-> Generator:

    stream_resp = StreamingResponse(
        response_gen=client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': user_message}
    ],
    temperature=0,
    stream=True
    ),
        source_nodes=[],
        metadata = {},
        response_txt="streaming response mock"
    )

    return stream_resp



