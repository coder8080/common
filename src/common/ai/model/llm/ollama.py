from os import environ

from langchain_ollama import ChatOllama

OLLAMA_URL = environ.get("OLLAMA_URL")
assert OLLAMA_URL

LLM_MODEL = environ.get("LLM_MODEL")
assert LLM_MODEL

llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_URL)
