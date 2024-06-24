from typing import Generator

from llama_index.core import (
    VectorStoreIndex,
    PromptTemplate,
)

from llama_index.core.base.response.schema import StreamingResponse

# workaround for streaming issues that llamaindex has
from openai import OpenAI

client = OpenAI()


PROMPT_TEMPALTE = """
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 
"""


def _format_metadata(metadata: dict) -> str:
    metadata_str = ""
    for key, value in metadata.items():
        if "date" not in key and "extension" not in key:
            metadata_str += f"{key}: {value}  \n"
    return metadata_str


def query(
    prompt: str,
    index: VectorStoreIndex,
    # prompt_template:PromptTemplate=PROMPT_TEMPALTE
) -> StreamingResponse:

    # -- re-visit this later --
    # qa_prompt = PromptTemplate(prompt_template)

    # get query engine (base query engine)
    doc_query_engine = index.as_query_engine(
        #response_mode="refine",
        use_async=False,
        streaming=True,
    )

    # prompts_dict = doc_query_engine.get_prompts()

    # lets try splitting this out too, so it can be used directly
    # Maybe some intermediates are messing with async?
    stream_response = doc_query_engine.query(prompt)

    # print("stream response type:  ", stream_response)
    # print("stream response gen type:  ", stream_response.response_gen)
    # Try to get docs
    # response_metadata = stream_response.metadata

    return stream_response

def get_query_engine(
        index: VectorStoreIndex):

    doc_query_engine = index.as_query_engine(
        #response_mode="refine",
        use_async=False,
        streaming=True,
    )

    return doc_query_engine

def manual_get_query_context(index: VectorStoreIndex,
                      user_message:str) -> str:
    retriever = index.as_retriever(choice_batch_size=5)
    nodes = retriever.retrieve(user_message)
    context = []
    for node in nodes:
        content = node.get_content()
        context.append(content)
    context = "\n".join(context)

    query = PROMPT_TEMPALTE.format(context_str=context, query_str=user_message)

    return query


def manual_query(query:str) -> StreamingResponse:
    # There are issues with llamaindex streaming response,
    # so just manually stream for now

    stream_resp = StreamingResponse(
        response_gen=client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': query}
            ],
            temperature=0,
            stream=True
            ),
        source_nodes=[],
        metadata = {},
        response_txt="streaming response mock"
    )

    return stream_resp


def retrieve(
    prompt: str,
    index: VectorStoreIndex,
    include_metadata: bool = True,
    include_content: bool = True,
    # prompt_template:PromptTemplate=PROMPT_TEMPALTE
) -> str:

    if not include_metadata and not include_content:
        # add logging later
        print("Warning - no context will be returned")

    retriever = index.as_retriever(choice_batch_size=5)

    nodes = retriever.retrieve(prompt)

    ref_content = []

    for node in nodes:

        if include_metadata:
            metadata = node.metadata
            print("metadata for node:\n  ", node.metadata)
            metadata_formatted = _format_metadata(metadata)
            ref_content.append(metadata_formatted)
        if include_content:
            content = node.get_content()
            ref_content.append(content)

    if len(ref_content) == 1:
        content_str = ref_content
    elif len(ref_content) == 0:
        content_str = "No reference found"
    else:
        content_str = "\n".join(ref_content)

    return content_str
