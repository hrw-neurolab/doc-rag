from beanie import PydanticObjectId
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

from src.config import CONFIG
from src.nlp.clients import CHAT_CLIENT
from src.resources.models import Chunk


__SYSTEM_MESSAGE = """\
You are a helpful assistant that can answer questions based on the provided resources.
A list of resources will be provided before every message, each containing a unique resource ID and its content.

You decide whether one of the resources is appropriate to answer the user's questions accurately and concisely.
IMPORTANT:
If a sentence or paragraph refers to a resource, cite the resource ID in **square brackets** at the end.
Example: "The capital of France is Paris [507f1f77bcf86cd799439011]."
If you use information from multiple resources, cite each resource ID in **separate** square brackets.
Example: "The capital of France is Paris [507f1f77bcf86cd799439011] [507f1f77bcf86cd799439012]."

If none matches the query, you can try to answer without resources, but then you MUST include a hint that you did not use resources.
In either case, DO NOT make up information - if you are not sure, refuse the answer and apologize kindly.\
"""

__HUMAN_MESSAGE = """\
Here are the current resources you may use to answer my question:
{resources}

{query}\
"""


__PROMPT_TEMPLATE = ChatPromptTemplate(
    [
        SystemMessagePromptTemplate.from_template(__SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(__HUMAN_MESSAGE),
    ]
)


__CHAIN = __PROMPT_TEMPLATE | CHAT_CLIENT | StrOutputParser()


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages = self.messages[-CONFIG.chat_client.max_history :] + messages

    def clear(self) -> None:
        self.messages = []


__MEMORY_HISTORY_STORE = {}


def __get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in __MEMORY_HISTORY_STORE:
        __MEMORY_HISTORY_STORE[session_id] = InMemoryHistory()
    return __MEMORY_HISTORY_STORE[session_id]


__HISTORY_CHAIN = RunnableWithMessageHistory(
    __CHAIN,
    __get_session_history,
    input_messages_key="query",
    history_messages_key="history",
)


async def stream_response(
    query: str, resources: list[Chunk], user_id: PydanticObjectId
):
    """Create a generator for the chat model.

    Args:
        query (str): The user's query.
        resources (list[Chunk]): List of resources to be used in the chat.
        user_id (PydanticObjectId): The ID of the user making the request.

    Yields:
        str: Streaming response from the chat model.
    """
    resources_str = "\n".join(
        f"- Resource ID: {str(resource.id)}, Content: {resource.content}"
        for resource in resources
    )

    variables = dict(query=query, resources=resources_str)
    config = RunnableConfig(configurable={"session_id": str(user_id)})

    async for chunk in __HISTORY_CHAIN.astream(variables, config):
        yield chunk


def clear_chat(user_id: PydanticObjectId) -> None:
    """Clear the chat history for the given user ID.

    Args:
        user_id (PydanticObjectId): The ID of the user whose chat history should be cleared.
    """
    history = __get_session_history(str(user_id))
    history.clear()
