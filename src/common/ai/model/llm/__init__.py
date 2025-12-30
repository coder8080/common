from os import environ

LLM_PROVIDER = environ.get("LLM_PROVIDER")

if LLM_PROVIDER == "ollama":
    from .ollama import llm
elif LLM_PROVIDER == "openai":
    from .openai import llm
elif LLM_PROVIDER == "openrouter":
    from .openrouter import llm
else:
    raise Exception(f"Unknown llm provider: {LLM_PROVIDER}")

__all__ = ["llm"]
