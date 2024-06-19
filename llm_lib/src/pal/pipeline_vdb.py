

from pal.query_vdb import query, retrieve
from pal.load_vdb import create_index, load_index 

from llama_index.llms.openai import OpenAI

from llama_index.core import (
    ServiceContext,
)

import os
from typing import List





def create_and_retreive_context_vdb(user_query:str, 
                                    model:str = "gpt-3.5-turbo",
                                    include_metadata:bool=True,
                                    include_content:bool=False) -> str:

    llm = OpenAI(
        temperature=0.2,
        openai_api_key=os.environ['OPENAI_API_KEY'],
        model = model
    )

    service_context = ServiceContext.from_defaults(
        llm = llm
    )

    # create_index(service_context)
    
    try:
        index = load_index()
        print("loaded existing index")
    except:
        try:
            print("attempting to create index")
            create_index(service_context)
            index = load_index()
            print("index created")
        except:
            print("index could not be created")
            raise ValueError("Index could not be created")

    content = retrieve(user_query, 
                       index, 
                       include_metadata=include_metadata,
                       include_content=include_content)

    return content



def create_and_query_vdb(user_query:str, model:str = "gpt-3.5-turbo"):

    llm = OpenAI(
        temperature=0.2,
        openai_api_key=os.environ['OPENAI_API_KEY'],
        model = model
    )

    service_context = ServiceContext.from_defaults(
        llm = llm
    )

    # create_index(service_context)
    
    try:
        index = load_index()
        print("loaded existing index")
    except:
        try:
            print("attempting to create index")
            create_index(service_context)
            index = load_index()
            print("index created")
        except:
            print("index could not be created")
            raise ValueError("Index could not be created")

    stream_response = query(user_query, index)

    return stream_response