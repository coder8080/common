from os import environ

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

OPENROUTER_API_KEY = environ.get("OPENROUTER_API_KEY")
assert OPENROUTER_API_KEY

LLM_MODEL = environ.get("LLM_MODEL")
assert LLM_MODEL

llm = ChatOpenAI(
    api_key=SecretStr(OPENROUTER_API_KEY),
    base_url="https://openrouter.ai/api/v1",
    model=LLM_MODEL,
)
