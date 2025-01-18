import time
from typing import Generator, List, Optional, Dict, Any
from dataclasses import dataclass, field
import asyncio

def mock_streaming_query():
    """
    This function is a mock of the response_generator_helper function in chat_utils.py
    It will return a mock stream of responses from the vdb.
    """
    for i in range(10):
        yield f"Mock response {i} \n"


def response_generator(user_message: str):
    # In a real scenario we would want to pass the user message to an LLM
    response = "Hello there! How can I assist you today?" * int(100) # 10,000 characters

    for word in response.split():
        yield word + " "


TokenGen = Generator[str, None, None]

@dataclass
class StreamingResponse:
    response_gen: TokenGen
    source_nodes: List = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    response_txt: Optional[str] = None


def mock_stream() -> Generator:
    response = "Hello there! How can I assist you today?" * int(100) # 10,000 characters

    for word in response.split():
        # this will bind the generator
        # time.sleep(0.01)
        # asyncio.sleep(0.1) <- would need to be in async
        yield word + " "


def rag_response_mock_generator(user_message:str):
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

        
        