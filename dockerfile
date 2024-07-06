# FROM python:3.11-slim

# RUN apt-get update -y
# RUN mkdir src


# WORKDIR /src
# COPY . /src

# RUN pip install --upgrade pip
# RUN pip install -r requirements/base.txt

# #ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# ENTRYPOINT ["fastapi", "dev"]

# docker build . -t htmx_chatbot
# docker run -p 8000:8000 htmx_chatbot
# ~220 MB image size
# uvicorn app.main:app --reload
# fastapi run app/main.py --port 8000

FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTESCODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements/base.txt


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# uvicorn app.main:app --host 0.0.0.0 --port 8000
# test prompt: What are some details about the technical writing course? Your response should be 2000 words

# docker build . -t htmx_chatbot

