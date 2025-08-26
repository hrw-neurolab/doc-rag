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
from src.nlp.inputclassifier import lang_check, retrieve_check
from src.resources.models import Chunk, Resource


__PROMPT_MESSAGES = {
    "en": {
        "system":  """\
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
            """,
        "human": """\
            Here are the current resources you may use to answer my question:
            {resources}

            {query}\
            """,

        "plain_system": """\
            You are a helpful, concise assistant. Answer conversationally.
            Do not cite documents or fabricate document-based claims in this mode.\
            """,
        "plain_human": """\
            {query}\
            """,
    },

    "de": {
        "system": """\
            Sie sind ein hilfreicher Assistent, der Fragen anhand der bereitgestellten Ressourcen beantworten kann.
            Vor jeder Nachricht wird eine Liste mit Ressourcen bereitgestellt, die jeweils eine eindeutige Ressourcen-ID und deren Inhalt enthält.

            Sie entscheiden, ob eine der Ressourcen geeignet ist, um die Fragen des Benutzers präzise und prägnant zu beantworten.
            WICHTIG:
            Wenn sich ein Satz oder Absatz auf eine Ressource bezieht, geben Sie die Ressourcen-ID am Ende in **eckigen Klammern** an.
            Beispiel: „Die Hauptstadt von Frankreich ist Paris [507f1f77bcf86cd799439011].“
            Wenn Sie Informationen aus mehreren Ressourcen verwenden, geben Sie jede Ressourcen-ID in **separaten** eckigen Klammern an.
            Beispiel: „Die Hauptstadt von Frankreich ist Paris [507f1f77bcf86cd799439011] [507f1f77bcf86cd799439012].“

            Wenn keine der Quellen mit der Suchanfrage übereinstimmt, können Sie versuchen, die Frage ohne Quellenangaben zu beantworten, müssen dann aber unbedingt einen Hinweis darauf geben, dass Sie keine Quellen verwendet haben.
            Erfinden Sie in keinem Fall Informationen – wenn Sie sich nicht sicher sind, lehnen Sie die Beantwortung der Frage ab und entschuldigen Sie sich höflich.\
            """,
        "human": """\
            Hier sind die aktuellen Ressourcen, die Sie zur Beantwortung meiner Frage verwenden können:
            {resources}

            {query}\
            """,
        "plain_system": """\
            Sie sind ein hilfsbereiter, prägnanter Assistent. Antworten Sie in einem dialogorientierten Stil.
            Zitieren Sie in diesem Modus keine Dokumente und erfinden Sie keine dokumentbasierten Behauptungen.\
            """,
        "plain_human": """\
            {query}\
            """,
    },
}

# __SYSTEM_MESSAGE = """\
# You are a helpful assistant that can answer questions based on the provided resources.
# A list of resources will be provided before every message, each containing a unique resource ID and its content.

# You decide whether one of the resources is appropriate to answer the user's questions accurately and concisely.
# IMPORTANT:
# If a sentence or paragraph refers to a resource, cite the resource ID in **square brackets** at the end.
# Example: "The capital of France is Paris [507f1f77bcf86cd799439011]."
# If you use information from multiple resources, cite each resource ID in **separate** square brackets.
# Example: "The capital of France is Paris [507f1f77bcf86cd799439011] [507f1f77bcf86cd799439012]."

# If none matches the query, you can try to answer without resources, but then you MUST include a hint that you did not use resources.
# In either case, DO NOT make up information - if you are not sure, refuse the answer and apologize kindly.\
# """

# __HUMAN_MESSAGE = """\
# Here are the current resources you may use to answer my question:
# {resources}

# {query}\
# """


# __PROMPT_TEMPLATE = ChatPromptTemplate(
#     [
#         SystemMessagePromptTemplate.from_template(__SYSTEM_MESSAGE),
#         MessagesPlaceholder(variable_name="history"),
#         HumanMessagePromptTemplate.from_template(__HUMAN_MESSAGE),
#     ]
# )


# __CHAIN = __PROMPT_TEMPLATE | CHAT_CLIENT | StrOutputParser()


# __PLAIN_SYSTEM_MESSAGE = """\
# You are a helpful, concise assistant. Answer conversationally.
# Do not cite documents or fabricate document-based claims in this mode.\
# """


# __PLAIN_HUMAN_MESSAGE = """\
# {query}\
# """


# __PLAIN_PROMPT_TEMPLATE = ChatPromptTemplate(
#     [
#         SystemMessagePromptTemplate.from_template(__PLAIN_SYSTEM_MESSAGE),
#         MessagesPlaceholder(variable_name="history"),
#         HumanMessagePromptTemplate.from_template(__PLAIN_HUMAN_MESSAGE),
#     ]
# )

# __PLAIN_CHAIN = __PLAIN_PROMPT_TEMPLATE | CHAT_CLIENT | StrOutputParser()



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


# __HISTORY_CHAIN = RunnableWithMessageHistory(
#     __CHAIN,
#     __get_session_history,
#     input_messages_key="query",
#     history_messages_key="history",
# )


# __PLAIN_HISTORY_CHAIN = RunnableWithMessageHistory(
#     __PLAIN_CHAIN,
#     __get_session_history,
#     input_messages_key="query",
#     history_messages_key="history",
# )


async def make_prompt_chain(language: str = "en",
                            needs_retrieval: bool = True):

    msgs = __PROMPT_MESSAGES[language]
    
    if needs_retrieval:
        system_msg = SystemMessagePromptTemplate.from_template(msgs["system"])
        human_msg = HumanMessagePromptTemplate.from_template(msgs["human"])
    else:
        system_msg = SystemMessagePromptTemplate.from_template(msgs["plain_system"])
        human_msg = HumanMessagePromptTemplate.from_template(msgs["plain_human"])

    prompt_template = ChatPromptTemplate(
        [
            system_msg,
            MessagesPlaceholder(variable_name="history"),
            human_msg,
        ]
    )
    
    chain = prompt_template | CHAT_CLIENT | StrOutputParser()
    
    history_chain = RunnableWithMessageHistory(
        chain,
        __get_session_history,
        input_messages_key="query",
        history_messages_key="history",
    )

    return history_chain


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
    language = await lang_check(query)
    needs_retrieval = await retrieve_check(query)

    chain = await make_prompt_chain(language=language,
                                    needs_retrieval=needs_retrieval)

    # Build title lookup for chunks' resources
    if needs_retrieval and resources:
        resource_ids = {c.resource for c in resources}
        resource_docs = await Resource.find({"_id": {"$in": list(resource_ids)}}).to_list()
        id_to_title = {str(r.id): r.title for r in resource_docs}

        def _title_for(resource_id) -> str:
            return id_to_title.get(str(resource_id), "Untitled")

        resources_str = "\n".join(
            f"- ID: {str(r.id)}, Title: {_title_for(r.resource)}, Page: {getattr(r, 'page_number', '?')}, Excerpt: {r.content}"
            for r in resources
        )
        
        variables = dict(query=query, resources=resources_str)
    
    # Plain mode or no chunks available
    else:
        variables = dict(query=query)

    config = RunnableConfig(configurable={"session_id": str(user_id)})

    async for chunk in chain.astream(variables, config):
        yield chunk


def clear_chat(user_id: PydanticObjectId) -> None:
    """Clear the chat history for the given user ID.

    Args:
        user_id (PydanticObjectId): The ID of the user whose chat history should be cleared.
    """
    history = __get_session_history(str(user_id))
    history.clear()
