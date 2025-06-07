from beanie import PydanticObjectId
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.config import CONFIG
from src.nlp.clients import CHAT_CLIENT
from src.resources.models import Chunk


__SYSTEM_MESSAGE = """\
You are a helpful assistant that can answer questions based on the provided resources.
A list of resources will be provided, each containing a unique resource ID and its content.
Use these resources to answer the user's questions accurately and concisely and do not make up information that is not present in the resources.

IMPORTANT:
Always cite the resource ID in **square brackets** when providing answers.
Example: "The capital of France is Paris [507f1f77bcf86cd799439011]."

Here are the resources:
{resources}
"""

__HUMAN_MESSAGE = "{query}"


__PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=__SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="history"),
        HumanMessage(content=__HUMAN_MESSAGE),
    ]
)


__CHAIN = __PROMPT_TEMPLATE | CHAT_CLIENT


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
        yield chunk.content
