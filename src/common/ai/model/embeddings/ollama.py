from os import environ

from langchain_ollama import OllamaEmbeddings

OLLAMA_URL = environ.get("OLLAMA_URL")
assert OLLAMA_URL

EMBEDDINGS_MODEL = environ.get("EMBEDDINGS_MODEL")
assert EMBEDDINGS_MODEL

embeddings = OllamaEmbeddings(model=EMBEDDINGS_MODEL, base_url=OLLAMA_URL)
