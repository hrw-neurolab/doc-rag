from beanie import PydanticObjectId
from fastapi import UploadFile

from src.resources.storage import store_resource_file
from src.nlp.embeddings import split_pdf, embed_chunks
from src.resources.models import PDFChunk, PDFResource, ResourceType


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
