import asyncio
from langdetect import detect
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     SystemMessagePromptTemplate,
# )
# from langchain_core.output_parsers import StrOutputParser
from transformers import pipeline
# from src.nlp.clients import CLASSIFIER_CLIENT
from src.config import CONFIG


# system_message = """\
# You are a helpful assistant that decides whether a query is knowledge-intensive and requires looking up resources.
# Except for simple chit-chats or short responses (e.g., "how are you","thank you", "good to know", "this is interesting"), most questions should fell into the category "requires resources" by default, and thereby a True as output.
# Return a clean boolean value True or False. Do NOT append any additional elaboration or explanation.\
# """

# human_message = """\
# Here is the query:

# {query}\
# """


# CLASSIFIER_PROMPT_TEMPLATE = ChatPromptTemplate(
#     [
#         SystemMessagePromptTemplate.from_template(system_message),
#         HumanMessagePromptTemplate.from_template(human_message),
#     ]
# )


# chain = CLASSIFIER_PROMPT_TEMPLATE | CLASSIFIER_CLIENT | StrOutputParser()

model_dir = "./backend/src/nlp"
model_name = CONFIG.input_classifier.model_name.split("/")[-1]
pipeline = pipeline(task="text-classification", model=f"{model_dir}/{model_name}")


async def lang_check(query: str = "") -> str:
    language = "de" if detect(query) == "de" else "en"
    return language

# async def retrieve_check(query: str = "", timeout_s: float = 3.0) -> bool:
#     prompt_vars = {"query": query}
#     try:
#         resp = await asyncio.wait_for(chain.ainvoke(prompt_vars), timeout=timeout_s)
#     except asyncio.TimeoutError:
#         return True  # safe fallback: retrieve
#     out = (resp or "").strip().split()[0].lower()
#     return out == "true"

async def retrieve_check(query: str = "") -> bool:
    if not query:
        return False
    
    prediction = pipeline(query)
    return True if prediction[0]["label"] == "LABEL_1" else False