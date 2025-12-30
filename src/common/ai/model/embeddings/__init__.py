from os import environ

EMBEDDINGS_PROVIDER = environ.get("EMBEDDINGS_PROVIDER")

if EMBEDDINGS_PROVIDER == "ollama":
    from .ollama import embeddings
elif EMBEDDINGS_PROVIDER == "openai":
    from .openai import embeddings
else:
    raise Exception(f"Unknown embeddings provider: {EMBEDDINGS_PROVIDER}")

__all__ = ["embeddings"]
