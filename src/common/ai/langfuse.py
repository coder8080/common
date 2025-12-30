from common.env import get_str_env
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

Langfuse(
    public_key=get_str_env("LANGFUSE_PUBLIC_KEY"),
    secret_key=get_str_env("LANGFUSE_SECRET_KEY"),
    host=get_str_env("LANGFUSE_HOST"),
)

langfuse = get_client()

langfuse_handler = CallbackHandler()
