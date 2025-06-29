# Tiny LLM factory
from __future__ import annotations

import os
from base64 import b64encode
from typing import Callable

from dotenv import find_dotenv, load_dotenv
from langchain_gigachat.chat_models.gigachat import GigaChat

# add more providers or local models when you have them, e.g. OpenAI, Ollama, Mistral etc.

load_dotenv(find_dotenv())
gpt_api_key = os.getenv("OPENAI_API_KEY")
giga_client_id = os.getenv("GIGA_CLIENT_ID")
giga_client_secret = os.getenv("GIGA_CLIENT_SECRET")

_CLIENT_BUILDERS: dict[str, Callable[[str], object]] = {}


def _build_gigachat(model_name: str) -> GigaChat:
    """GigaChat-specific LLM-client builder."""
    client_id = os.getenv("GIGA_CLIENT_ID")
    client_secret = os.getenv("GIGA_CLIENT_SECRET")
    creds = b64encode(f"{client_id}:{client_secret}".encode()).decode()

    return GigaChat(
        credentials=creds,
        scope="GIGACHAT_API_CORP",
        model=model_name,
        verify_ssl_certs=False,
    )


_CLIENT_BUILDERS["gigachat"] = _build_gigachat


def get_llm(model_id: str) -> object:
    """
    Model getter interface.
    model_id examples: 'gigachat:GigaChat-2-Max', 'openai:gpt-4o', etc.
    """
    provider, _, name = model_id.partition(":")
    try:
        builder = _CLIENT_BUILDERS[provider.lower()]
    except KeyError:
        raise ValueError(f"Unknown LLM provider '{provider}'")

    return builder(name)
