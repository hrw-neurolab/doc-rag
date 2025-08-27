from langchain_ollama import OllamaEmbeddings, ChatOllama

from src.config import CONFIG, ModelProvider


if CONFIG.embedding_client.model_provider == ModelProvider.OLLAMA:
    EMBEDDING_CLIENT = OllamaEmbeddings(
        model=CONFIG.embedding_client.model_name,
        base_url=CONFIG.embedding_client.base_url,
        num_ctx=CONFIG.embedding_client.num_ctx,
        temperature=CONFIG.embedding_client.temperature,
    )
else:
    raise ValueError(
        f"Unsupported embedding model provider: {CONFIG.embedding_client.model_provider}"
    )


if CONFIG.chat_client.model_provider == ModelProvider.OLLAMA:
    CHAT_CLIENT = ChatOllama(
        model=CONFIG.chat_client.model_name,
        base_url=CONFIG.chat_client.base_url,
        num_ctx=CONFIG.chat_client.num_ctx,
        temperature=CONFIG.chat_client.temperature,
    )
    CLASSIFIER_CLIENT = ChatOllama(
        model="llama3.2",
        base_url=CONFIG.chat_client.base_url,
        num_ctx=2048,
        temperature=0.2,
    )
else:
    raise ValueError(
        f"Unsupported chat model provider: {CONFIG.chat_client.model_provider}"
    )
