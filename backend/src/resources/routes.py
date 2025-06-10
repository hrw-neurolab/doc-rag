from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from src.auth.dependencies import current_user
import src.resources.database as resources_db
from src.resources.models import (
    PDFChunk,
    PDFResource,
    Resource,
    WebpageChunk,
    WebpageResource,
)
from src.users.models import UserDB


router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/pdf")
async def create_pdf_resource(
    file: UploadFile, user: Annotated[UserDB, Depends(current_user)]
):
    """Create a new PDF resource.

    Args:
        file (UploadFile): The PDF file to be processed.
        user (UserDB): The user creating the resource.

    Returns:
        PDFResource: The created PDF resource.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    return await resources_db.create_pdf_resource(file=file, user_id=user.id)


@router.get("")
async def get_resources(
    user: Annotated[UserDB, Depends(current_user)],
    query: str = None,
) -> list[Resource]:
    """Get all resources for the current user.

    Args:
        user (UserDB): The user requesting the resources.
        query (str, optional): Optional search query to filter resources.

    Returns:
        list[Resource]: A list of resources associated with the user.
    """
    return await resources_db.get_resources(user.id, query)


@router.get("/{resource_id}")
async def get_resource_by_id(
    resource_id: PydanticObjectId,
    user: Annotated[UserDB, Depends(current_user)],
) -> PDFResource | WebpageResource:
    """Get a specific resource by its ID.

    Args:
        resource_id (PydanticObjectId): The ID of the resource to retrieve.
        user (UserDB): The user requesting the resource.

    Returns:
        Resource: The requested resource.
    """
    return await resources_db.get_resource_by_id(resource_id, user.id)


@router.get("/chunk/{chunk_id}", response_model_exclude={"embedding"})
async def get_chunk_by_id(
    chunk_id: PydanticObjectId,
    user: Annotated[UserDB, Depends(current_user)],
) -> PDFChunk | WebpageChunk:
    """Get a specific chunk by its ID.

    Args:
        chunk_id (PydanticObjectId): The ID of the chunk to retrieve.
        user (UserDB): The user requesting the chunk.

    Returns:
        Chunk: The requested chunk.
    """
    return await resources_db.get_chunk_by_id(chunk_id, user.id)


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: PydanticObjectId,
    user: Annotated[UserDB, Depends(current_user)],
) -> None:
    """Delete a specific resource by its ID.

    Args:
        resource_id (PydanticObjectId): The ID of the resource to delete.
        user (UserDB): The user requesting the deletion.

    Raises:
        HTTPException: If the resource does not exist or does not belong to the user.
    """
    await resources_db.delete_resource_by_id(resource_id, user.id)
