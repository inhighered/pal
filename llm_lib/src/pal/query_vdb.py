from llama_index.core import (
    VectorStoreIndex,
    PromptTemplate,
)



PROMPT_TEMPALTE = """
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 
"""



def query(prompt: str,
          index: VectorStoreIndex,
          #prompt_template:PromptTemplate=PROMPT_TEMPALTE
          ):

    # -- re-visit this later -- 
    # qa_prompt = PromptTemplate(prompt_template)

    doc_query_engine = index.as_query_engine(
        response_mode = "refine",
        use_async = True,
        streaming=True,
    )

    #prompts_dict = doc_query_engine.get_prompts()

    stream_response = doc_query_engine.query(prompt)

    # Try to get docs
    #response_metadata = stream_response.metadata

    return stream_response

def retrieve(
        prompt: str,
        index: VectorStoreIndex
        #prompt_template:PromptTemplate=PROMPT_TEMPALTE
        ):
    
    retriever = index.as_retriever(choice_batch_size=5)

    nodes = retriever.retrieve(prompt)

    content = []

    for node in nodes:
        content.append(node.get_content())

    content_str = "\n".join(content)

    return content_str

