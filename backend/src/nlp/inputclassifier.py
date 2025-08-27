import re
import asyncio
from langdetect import detect
from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

from src.nlp.clients import CLASSIFIER_CLIENT


system_message = """\
You are a helpful assistant that decides whether a query is knowledge-intensive and requires looking up resources.

Return a clean boolean value True or False. Do NOT append any additional elaboration or explanation.\
"""

human_message = """\
Here is the query:

{query}\
"""


CLASSIFIER_PROMPT_TEMPLATE = ChatPromptTemplate(
    [
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(human_message),
    ]
)

# CLASSIFIER_CLIENT = ChatOllama(
#         model="llama3.2",
#         base_url="http://localhost:11434",
#         num_ctx=2048,
#         temperature=0.1,
#     )

# if CONFIG.chat_client.model_provider == ModelProvider.OLLAMA:
#     CHAT_CLIENT = ChatOllama(
#         model=CONFIG.chat_client.model_name,
#         base_url=CONFIG.chat_client.base_url,
#         num_ctx=CONFIG.chat_client.num_ctx,
#         temperature=CONFIG.chat_client.temperature,
#     )
# else:
#     raise ValueError(
#         f"Unsupported chat model provider: {CONFIG.chat_client.model_provider}"
#     )

chain = CLASSIFIER_PROMPT_TEMPLATE | CLASSIFIER_CLIENT | StrOutputParser()


_RULE_CHITCHAT = re.compile(
    r"\b(thanks|thank you|hi|hello|hey|bye|goodbye|sorry|how are you|who are you)\b",
    re.IGNORECASE,
)

def _rule_route(query: str) -> bool:
    # Return False = no retrieval for obvious chit-chat/meta
    if _RULE_CHITCHAT.search(query or ""):
        return False
    return None  # undecided

async def _llm_route(query: str, timeout_s: float = 3.0) -> bool:
    prompt_vars = {"query": query}
    try:
        resp = await asyncio.wait_for(chain.ainvoke(prompt_vars), timeout=timeout_s)
    except asyncio.TimeoutError:
        return True  # safe fallback: retrieve
    out = (resp or "").strip().split()[0].lower()
    print(f"------====== {out} ======------")
    return out == "true"

async def lang_check(query: str = "") -> str:
    language = "de" if detect(query) == "de" else "en"
    return language

async def retrieve_check(query: str = "") -> bool:
    # 1) cheap rules
    rule = _rule_route(query)
    if rule is not None:
        return rule
    # 2) LLM fallback
    return await _llm_route(query)