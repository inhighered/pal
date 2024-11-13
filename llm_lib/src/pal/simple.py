from openai import OpenAI
from ollama import Client
import os

if os.getenv("OPENAI_API_KEY") is None:
    client = Client(host=os.getenv("OLLAMA_BASE_URL"))
else:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def open_ai_stream(message: str):

    if os.getenv("OPENAI_API_KEY") is None:
        stream = client.chat(
            model="llama3.2:1b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{message}"},
            ],
            stream=True,
        )
    else:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{message}"},
            ],
            stream=True,
        )

    return stream


# stream = query_stream()
# print(stream)
# for chunk in stream:
#     if chunk.choices[0].delta.content is not None:
#         print(chunk.choices[0].delta.content, end="")
