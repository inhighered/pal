from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    get_response_synthesizer,
    #ServiceContext,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import FlatReader

from pal.llama_index_cust_parser import HeadingMarkdownNodeParser

import os
import shutil
from pathlib import Path


def get_available_files(data_path: str = "data") -> list:
    documents = os.listdir(data_path)
    return documents

def clear_files(data_path: str = "data") -> None:
    for document in os.listdir(data_path):
        os.remove(f"data/{document}")

def add_test_files(data_path: str = "data") -> None:
    for document in os.listdir(data_path):
        if document.endswith(".md"):
            shutil.copy(f"data/{document}", f"llm_lib/data/{document}")

def create_index(
    service_context: dict, # now settings,
    data_path: str = "data",
    store_name: str = "class_documents_index",
) -> None:

    documents = []
    for document in os.listdir(data_path):
        if document.endswith(".md"):
            documents.extend(FlatReader().load_data(Path(f"data/{document}")))
    # documents = FlatReader().load_data(Path("data/course.md"))

    if len(documents) == 0:
        raise ValueError("No documents found in data path")
    # documents = SimpleDirectoryReader(data_path).load_data()

    # Apply custom markdown parser
    parser = HeadingMarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(documents, heading_level=2)

    print(f"generated nodes {len(nodes)}")

    response_synthesizer = get_response_synthesizer(
        use_async=True,
    )

    index = VectorStoreIndex(
        nodes,
        #service_context=service_context,
        embed_model=service_context.embed_model,
        response_synthesizer=response_synthesizer,
        show_progress=True,
    )

    index.storage_context.persist(f"vector_db/{store_name}")


def load_index(store_name: str = "class_documents_index") -> VectorStoreIndex:

    # load index if exists:
    try:
        print("trying to load index")
        storage_context = StorageContext.from_defaults(
            persist_dir=f"vector_db/{store_name}"
        )
        index = load_index_from_storage(storage_context)
        print(f"loaded index {store_name}")
    except Exception as e:
        print(e)
        raise ValueError(f"Index {store_name} not found")

    return index


def delete_index(store_name: str = "class_documents_index") -> bool:
    index_deleted = False

    try:
        shutil.rmtree(f"vector_db/{store_name}", ignore_errors=True)
        index_deleted = True
    except:
        pass

    return index_deleted



def get_index_exists_status():
    try:
        index = load_index()
        return True
    except:
        return False


def create_index_if_not_exists(model:str = "gpt-3.5-turbo",
                               llm:OpenAI = None,
                               embedding:OpenAIEmbedding = None,
                               service_context: dict = None # now settings
                               ):
    if not llm:
        llm = OpenAI(
            temperature=0.2,
            openai_api_key=os.environ['OPENAI_API_KEY'],
            model = model
        )

    if not embedding:
        embedding = OpenAIEmbedding(
            model="text-embedding-3-small",
            openai_api_key=os.environ['OPENAI_API_KEY'],
            embed_batch_size=100
        )

    if not service_context:
        # service_context = ServiceContext.from_defaults(
        #     llm = llm
        # )
        Settings.llm = llm
        Settings.embed_model = embedding

    

    try:
        index = load_index()
        print("loaded existing index")
    except:
        try:
            print("attempting to create index")
            create_index(Settings)
            index = load_index()
            print("index created")
        except:
            print("index could not be created")
            raise ValueError("Index could not be created")
    
    return index
