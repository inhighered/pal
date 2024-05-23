
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    get_response_synthesizer,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)

import os
import shutil



def create_index(service_context:ServiceContext,
                 data_path:str = 'data',
                 store_name:str = "class_documents_index",
                 ):
    
    documents = SimpleDirectoryReader(data_path).load_data()

    response_synthesizer = get_response_synthesizer(
        use_async=True,
    )


    index = VectorStoreIndex(
        documents,
        service_context = service_context,
        response_synthesizer = response_synthesizer,
        show_progress = True,
    )


    index.storage_context.persist(f"vector_db/{store_name}")


def load_index(store_name:str = "class_documents_index"):
    
    # load index if exists:
    try:
        print("trying to load index")
        storage_context = StorageContext.from_defaults(persist_dir = f"vector_db/{store_name}")
        index = load_index_from_storage(storage_context)
        print(f"loaded index {store_name}")
    except Exception as e:
        print(e)
        raise ValueError(f"Index {store_name} not found")
    
    return index



def delete_index(store_name:str = "class_documents_index"):

    shutil.rmtree(f"vector_db/{store_name}", ignore_errors=True)
    
    return 

