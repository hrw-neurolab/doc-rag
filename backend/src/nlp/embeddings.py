from beanie import PydanticObjectId
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_mongodb.pipelines import vector_search_stage
from fastapi import HTTPException, status
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CONFIG
from src.nlp.clients import EMBEDDING_CLIENT
from src.resources.models import Chunk, PDFChunk


__PDF_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=CONFIG.embedding_client.chunk_size,
    chunk_overlap=CONFIG.embedding_client.chunk_overlap,
    length_function=len,
)


async def split_pdf(file_path: str) -> tuple[list[Document], int]:
    """Create raw chunks for a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        tuple[list[Document], int]: A tuple containing the raw chunks and the total number of pages.
    """
    loader = PyPDFLoader(file_path)
    pages = await loader.aload()

    if not pages:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The PDF file is empty or could not be loaded.",
        )

    total_pages = pages[0].metadata.get("total_pages", 0)
    raw_chunks = __PDF_SPLITTER.split_documents(pages)

    return raw_chunks, total_pages


async def embed_chunks(raw_chunks: list[Document]) -> list[list[float]]:
    """Create embedding vectors for the raw chunks.

    Args:
        raw_chunks (list[Document]): List of raw chunks from the PDF.

    Returns:
        list[list[float]]: List of embedding vectors for each chunk.
    """
    contents = [chunk.page_content for chunk in raw_chunks]
    return await EMBEDDING_CLIENT.aembed_documents(contents)


async def similarity_search(
    query: str,
    user_id: PydanticObjectId,
    resource_ids: list[PydanticObjectId] | None,
) -> list[PDFChunk | Chunk]:
    """Perform a similarity search for the given query.

    Args:
        query (str): The query string to search for.
        user_id (PydanticObjectId): The ID of the user making the request.
        resource_ids (list[PydanticObjectId]): List of resource IDs to search within. (Optional)

    Returns:
        list[Chunk]: List of chunks that match the query.
    """
    query_embedding = await EMBEDDING_CLIENT.aembed_query(query)

    pre_filter = {"user_id": user_id}

    if resource_ids:
        pre_filter["resource"] = {"$in": resource_ids}

    search_stage = vector_search_stage(
        query_embedding,
        CONFIG.mongo.search_index_field,
        CONFIG.mongo.search_index_name,
        CONFIG.mongo.search_top_k,
        pre_filter,
    )

    pipeline = [search_stage]

    results = await Chunk.aggregate(pipeline).to_list()

    chunks = []
    for result in results:
        if "page_number" in result:
            chunks.append(PDFChunk(**result))
        else:
            chunks.append(Chunk(**result))

    return chunks
