

from pal.query_vdb import query, retrieve, get_query_engine
from pal.load_vdb import create_index, load_index, create_index_if_not_exists

from llama_index.core import (
    Settings,
    # ServiceContext,
)

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import os
from typing import List



# TODO - Consolidate these later

def create_and_retreive_context_vdb(user_query:str, 
                                    model:str = "gpt-3.5-turbo",
                                    include_metadata:bool=True,
                                    include_content:bool=False) -> str:

    llm = OpenAI(
        temperature=0.2,
        openai_api_key=os.environ['OPENAI_API_KEY'],
        model = model
    )

    # service_context = ServiceContext.from_defaults(
    #     llm = llm
    # )

    embedding = OpenAIEmbedding(
            model="text-embedding-3-small",
            openai_api_key=os.environ['OPENAI_API_KEY'],
            embed_batch_size=100
        )


    Settings.llm = llm
    Settings.embed_model = embedding

    index = create_index_if_not_exists(
        model=model,
        llm=llm, 
        embedding=embedding,
        service_context=Settings
        )

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

    # service_context = ServiceContext.from_defaults(
    #     llm = llm
    # )    

    embedding = OpenAIEmbedding(
            model="text-embedding-3-small",
            openai_api_key=os.environ['OPENAI_API_KEY'],
            embed_batch_size=100
        )


    Settings.llm = llm
    Settings.embed_model = embedding

    index = create_index_if_not_exists(
        model=model,
        llm=llm, 
        embedding=embedding,
        service_context=Settings
        )
    
    query_engine = get_query_engine(index)

    return query_engine, user_query
    #stream_response = query(user_query, index)

    #return stream_response


def create_index_default_context(model:str = "gpt-3.5-turbo"):
    llm = OpenAI(
        temperature=0.2,
        openai_api_key=os.environ['OPENAI_API_KEY'],
        model = model
    )

    # service_context = ServiceContext.from_defaults(
    #     llm = llm
    # )

    embedding = OpenAIEmbedding(
            model="text-embedding-3-small",
            openai_api_key=os.environ['OPENAI_API_KEY'],
            embed_batch_size=100
        )


    Settings.llm = llm
    Settings.embed_model = embedding

    index = create_index_if_not_exists(
        model=model,
        llm=llm, 
        embedding=embedding,
        service_context=Settings
        )
    
    return index