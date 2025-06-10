from datetime import datetime
from enum import Enum
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ResourceType(str, Enum):
    PDF = "pdf"
    WEBPAGE = "webpage"


class Resource(Document):
    title: str
    type: ResourceType
    user: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "resources"
        is_root = True


class PDFResource(Resource):
    total_pages: int


class WebpageResource(Resource):
    url: HttpUrl


class Chunk(Document):
    user: Annotated[PydanticObjectId, Indexed()]
    resource: Annotated[PydanticObjectId, Indexed()]
    content: str
    embedding: list[float]
    index: int

    class Settings:
        name = "chunks"
        is_root = True


class PDFChunk(Chunk):
    page_number: int


class WebpageChunk(Chunk): ...
