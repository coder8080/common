from os import environ

from langchain_openai import ChatOpenAI

assert environ.get("OPENAI_API_KEY")

LLM_MODEL = environ.get("LLM_MODEL")
assert LLM_MODEL

llm = ChatOpenAI(model=LLM_MODEL)
