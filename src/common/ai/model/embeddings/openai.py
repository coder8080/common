from os import environ

from langchain_openai import OpenAIEmbeddings

assert environ.get("OPENAI_API_KEY")

EMBEDDINGS_MODEL = environ.get("EMBEDDINGS_MODEL")
assert EMBEDDINGS_MODEL

embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
