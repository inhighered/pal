# Utils for getting initial documents
from typing import List

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)

from app.utils.database.models import (
    Doc,
)

from app.utils.database.db_utils import (
    with_connection,
)

from psycopg import Connection

from logging import getLogger
_logger = getLogger(__name__)

# need either files path, or vector db connection


# ---------- General Docs Queries ----------

@with_connection
def get_latest_docs(conn:Connection) -> List[Doc]:
    sql = """SELECT 
        doc_group_id,
        doc_name,
        doc_location, 
        doc_content, 
        doc_active,
        doc_hash
    FROM 
        app.docs
    WHERE 
        doc_active = 1
    ORDER BY doc_group_id DESC"""
    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchall()
    docs = []
    for results in results_tuple:
        doc_group_id, doc_name, doc_location, doc_content, doc_active, doc_hash = results
        doc = Doc(doc_group_id, doc_name, doc_location, doc_content, doc_active, doc_hash)
        docs.append(doc) 
    return docs

def get_latest_doc_group_from_docs(docs: List[Doc]) -> int:
    doc_group_id = 0
    for doc in docs:
        if doc.doc_group_id > doc_group_id:
            doc_group_id = doc.doc_group_id

    return doc_group_id

@with_connection
def get_latest_doc_group(conn:Connection) -> int:
    sql = """SELECT 
        doc_group_id
    FROM 
        app.docs
    where doc_active = 1
    ORDER BY doc_group_id DESC
    LIMIT 1"""
    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchall()

    _logger.debug(f"Latest doc results: \n {results_tuple}")

    if results_tuple != [[]] and results_tuple != []:
        doc_group_id = results_tuple[0][0]
    else:
        doc_group_id = 0

    return doc_group_id




# -------------------- Handle VDB Index ---------------------


# if we have files - we either need to populate the db with them, or check if they are in the vdb

def load_index(store_name: str = "class_documents_index") -> VectorStoreIndex:
    # for now this name will be static

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

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_docs_from_index(index: VectorStoreIndex) -> List[Doc]:

    docs = []
    doc_group_id = get_latest_doc_group()
    _logger.debug(f"Getting docs from index: {index}")
    _logger.debug(f"Index doc info: {index.ref_doc_info}")

    for key in index.ref_doc_info.keys():
        doc_name = index.ref_doc_info[key].metadata['filename']
        # we don't really have a filepath set up, so we'll use local for now-
        # doc_location = index.ref_doc_info[key].metadata['file_path']
        doc_location = f"data/{doc_name}"
        # read the doc and get content
        doc_content = read_file(doc_location)
        _logger.debug(f"Doc content: \n {doc_content}")
        doc_active = 1

        doc = Doc(
            doc_group_id,
            doc_name,
            doc_location,
            doc_content,
            doc_active
        )

        docs.append(doc)

    return docs



@with_connection
def init_existing_docs(conn:Connection) -> List[Doc]:

    docs = []

    sql = """SELECT count(*)
    from app.docs"""

    cur = conn.cursor()
    cur.execute(sql)
    results_tuple = cur.fetchone()
    _logger.debug(f"Existing docs in db: \n {results_tuple}")

    if results_tuple[0] < 1:
        _logger.debug("No existing docs in db, trying to create them")
        index = load_index()
        docs = get_docs_from_index(index)
        for doc in docs:
            doc.insert()

    else:
        _logger.debug("Existing docs in db, returning them")
        docs = get_latest_docs()

    return docs