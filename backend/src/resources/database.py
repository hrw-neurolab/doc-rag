from beanie import PydanticObjectId
from beanie.operators import RegEx
from fastapi import HTTPException, UploadFile, status
from typing import Optional, List

from src.resources.storage import store_resource_file
from src.nlp.embeddings import split_pdf, embed_chunks
from src.resources.models import Chunk, PDFChunk, PDFResource, Resource, ResourceType


async def create_pdf_resource(file: UploadFile, user_id: PydanticObjectId):
    """Create a new PDF resource.

    Args:
        file (UploadFile): The PDF file to be processed.
        user_id (PydanticObjectId): The ID of the user creating the resource.

    Returns:
        PDFResource: The created PDF resource.
    """
    resource_id = PydanticObjectId()

    file_path = await store_resource_file(
        file=file,
        user_id=user_id,
        resource_type=ResourceType.PDF,
        resource_id=resource_id,
    )

    raw_chunks, total_pages = await split_pdf(file_path)

    pdf_resource = await PDFResource(
        id=resource_id,
        title=file.filename,
        type=ResourceType.PDF,
        user=user_id,
        total_pages=total_pages,
    ).create()

    embeddings = await embed_chunks(raw_chunks)

    pdf_chunks = []
    for i, raw_chunk in enumerate(raw_chunks):
        pdf_chunk = PDFChunk(
            user=user_id,
            resource=resource_id,
            content=raw_chunk.page_content,
            embedding=embeddings[i],
            index=i,
            page_number=raw_chunk.metadata.get("page", 0),
        )
        pdf_chunks.append(pdf_chunk)

    await PDFChunk.insert_many(pdf_chunks)

    return pdf_resource


# async def get_resources(user_id: PydanticObjectId, query: str | None) -> list[Resource]:
async def get_resources(user_id: PydanticObjectId, query: Optional[str]) -> List[Resource]:
    """Get all resources for the current user.

    Args:
        user_id (PydanticObjectId): The ID of the user requesting the resources.
        query (str | None): Optional search query to filter resources.

    Returns:
        list[Resource]: A list of resources associated with the user.
    """
    args = [Resource.user == user_id]

    if query:
        args.append(RegEx(Resource.title, f".*{query}.*", options="i"))

    return await Resource.find(*args, with_children=True).to_list()


async def get_resource_by_id(
    resource_id: PydanticObjectId, user_id: PydanticObjectId
) -> Resource:
    """Get a specific resource by its ID.

    Args:
        resource_id (PydanticObjectId): The ID of the resource to retrieve.
        user_id (PydanticObjectId): The ID of the user requesting the resource.

    Returns:
        Resource: The requested resource.
    """
    resource = await Resource.find_one(
        Resource.id == resource_id, Resource.user == user_id, with_children=True
    )

    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID {resource_id} not found for user {user_id}.",
        )

    return resource


async def get_chunk_by_id(
    chunk_id: PydanticObjectId, user_id: PydanticObjectId
) -> PDFChunk:
    """Get a specific chunk by its ID.

    Args:
        chunk_id (PydanticObjectId): The ID of the chunk to retrieve.
        user_id (PydanticObjectId): The ID of the user requesting the chunk.

    Returns:
        PDFChunk: The requested chunk.
    """
    chunk = await Chunk.find_one(
        Chunk.id == chunk_id, Chunk.user == user_id, with_children=True
    )

    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with ID {chunk_id} not found for user {user_id}.",
        )

    return chunk


async def delete_resource_by_id(
    resource_id: PydanticObjectId, user_id: PydanticObjectId
) -> None:
    """Delete a specific resource by its ID.

    Args:
        resource_id (PydanticObjectId): The ID of the resource to delete.
        user_id (PydanticObjectId): The ID of the user requesting the deletion.

    Raises:
        HTTPException: If the resource does not exist or does not belong to the user.
    """
    resource = await get_resource_by_id(resource_id, user_id)
    await resource.delete()
    await Chunk.find(Chunk.resource == resource_id, with_children=True).delete()
