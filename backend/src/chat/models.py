from pydantic import BaseModel
from beanie import PydanticObjectId


class ResourceChatBody(BaseModel):
    query: str
    resource_ids: list[PydanticObjectId] = None
