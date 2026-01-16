import base64
import io
import zlib
import json
import pandas as pd
from beanie import PydanticObjectId
from pymongo.operations import SearchIndexModel
from pymongo.errors import OperationFailure
# from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_mongodb.pipelines import vector_search_stage
from langchain_text_splitters import TokenTextSplitter
from langchain_unstructured import UnstructuredLoader
from fastapi import HTTPException, status
from typing import Union, List, Optional

# import nltk
from src.config import CONFIG
from src.nlp.clients import EMBEDDING_CLIENT
from src.nlp.mmr import MMRSelector
from src.nlp.textcleaner import TextCleaner
from src.resources.models import Chunk, PDFChunk

# __PDF_SPLITTER = RecursiveCharacterTextSplitter(
#     chunk_size=CONFIG.embedding_client.chunk_size,
#     chunk_overlap=CONFIG.embedding_client.chunk_overlap,
#     length_function=len,
# )
__PDF_SPLITTER = TokenTextSplitter(
    chunk_size=CONFIG.embedding_client.chunk_size,
    chunk_overlap=CONFIG.embedding_client.chunk_overlap,
    encoding_name="cl100k_base",
)

__MMR_SELECTOR = MMRSelector(
    final_k=CONFIG.embedding_client.mmr_final_k,
    lambda_param=CONFIG.embedding_client.mmr_lambda_param,
    similarity_threshold=CONFIG.embedding_client.mmr_similarity_threashold
)

__TEXT_CLEANER = TextCleaner(
    take=CONFIG.embedding_client.textcleaner_take,
    min_ratio=CONFIG.embedding_client.textcleaner_ratio
)

# nltk.download('punkt')
# nltk.download('punkt_tab')


# class SentenceTextSplitter(TextSplitter):
#     def __init__(self, sentences_per_chunk=10, overlap=2):
#         super().__init__()
#         self.sentences_per_chunk = sentences_per_chunk
#         self.overlap = overlap

#     def split_text(self, text: str) -> list[str]:
#         sentences = nltk.tokenize.sent_tokenize(text)
#         chunks = []
#         step = max(1, self.sentences_per_chunk - self.overlap)

#         for i in range(0, len(sentences), step):
#             chunk = " ".join(sentences[i:i + self.sentences_per_chunk])
#             chunks.append(chunk.strip())

#         return chunks

# __PDF_SPLITTER = SentenceTextSplitter(sentences_per_chunk=12, overlap=2)


def html_to_markdown(html_str: str) -> str:
    """Converts one or multiple HTML table strings to clean Markdown."""
    try:
        # pd.read_html returns a list of DataFrames for all <table> tags found
        dfs = pd.read_html(io.StringIO(html_str))
        if not dfs:
            return ""
        
        # Join multiple tables with double newlines
        return "\n\n".join([df.to_markdown(index=False) for df in dfs])
    except Exception:
        # If conversion fails, return the raw text to avoid losing data
        return html_str


async def create_search_index():
    """Create a search index for the Chunk collection.
    This function checks if the search index already exists, and if not, it creates one.
    If the collection does not exist, it creates a dummy document to initialize the collection first.

    Raises:
        OperationFailure: If there is an error creating the search index.
    """
    # collection = Chunk.get_motor_collection()
    collection = Chunk.get_pymongo_collection()
    indexes = await collection.list_search_indexes().to_list()

    if len(indexes) > 0 and indexes[-1]["name"] == "embedding_index":
        return

    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": CONFIG.mongo.search_index_dimensions,
                    "path": CONFIG.mongo.search_index_field,
                    "similarity": CONFIG.mongo.search_index_similarity,
                },
                {
                    "type": "filter",
                    "path": "user",
                },
                {
                    "type": "filter",
                    "path": "resource",
                },
            ]
        },
        name=CONFIG.mongo.search_index_name,
        type="vectorSearch",
    )

    try:
        await collection.create_search_index(search_index_model)
        return

    except OperationFailure as e:
        if e.details.get("codeName") != "NamespaceNotFound":
            raise e

    # Insert a dummy document to create the collection
    result = await collection.insert_one({})
    await collection.delete_one({"_id": result.inserted_id})

    # Retry creating the search index
    await collection.create_search_index(search_index_model)


# async def split_pdf(file_path: str) -> tuple[list[Document], int]:
#     """Create raw chunks for a PDF file.

#     Args:
#         file_path (str): Path to the PDF file.

#     Returns:
#         tuple[list[Document], int]: A tuple containing the raw chunks and the total number of pages.
#     """
#     loader = PyPDFLoader(file_path)
#     pages = await loader.aload()


#     # Clean page contents and ensure page metadata
#     raw_page_texts = [p.page_content for p in pages]
#     cleaned_texts = __TEXT_CLEANER.clean_pages(raw_page_texts)
#     for i, p in enumerate(pages):
#         p.page_content = cleaned_texts[i]
#         # ensure 1-based page number is present
#         p.metadata["page"] = p.metadata.get("page", i + 1)

#     if not pages:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="The PDF file is empty or could not be loaded.",
#         )

#     total_pages = pages[0].metadata.get("total_pages", 0)
#     raw_chunks = __PDF_SPLITTER.split_documents(pages)

#     return raw_chunks, total_pages

async def split_pdf(file_path: str) -> tuple[list[Document], int]:
    """Create raw chunks for a PDF file using the modern langchain_unstructured loader.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        tuple[list[Document], int]: A tuple containing the raw chunks and the total number of pages.
    """
    # Initialize the modern UnstructuredLoader
    loader = UnstructuredLoader(
        file_path=file_path,
        strategy="fast",
        partition_via_api=False,
        infer_table_structure=True,   # Critical for keeping tables together
        languages=["deu", "eng"],
        skip_infer_table_types=["Header", "Footer"],
        
        # --- THE FIX: NATIVE CHUNKING ---
        chunking_strategy="by_title",   # Groups elements logically under headings
        max_characters=2000,            # Target size for each chunk
        combine_text_under_n_chars=500, # Merges small snippets into the next chunk
        multipage_sections=True,        # Allows chunks to span across pages if logical
        multiprocessing_context="fork", # or "spawn" depending on OS
        max_partitionbatch_size=5,      # Process in batches of 5 pages
        workers=4,                      # Use 4 CPU cores
    )

    try:
        # langchain_unstructured supports async aload natively
        chunks = await loader.aload()
    except Exception as e:
        # Catch errors if local dependencies (tesseract/poppler) are missing
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF with Unstructured: {str(e)}",
        )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The PDF file is empty or could not be loaded.",
        )

    max_page = 0
    
    # for chunk in chunks:
    #     # 1. Page Metadata
    #     current_page = chunk.metadata.get("page_number", 1)
    #     chunk.metadata["page"] = current_page
    #     if current_page > max_page:
    #         max_page = current_page

    #     category = chunk.metadata.get("category", "Text")
        # print("\n\n\n\n\n", chunk.metadata, "\n\n\n\n\n")
        # print("\n\n\n\n\n", category, "\n\n\n\n\n")
        # 2. Table Protection
        # if category == "Table":
        #     # STRATEGY A: Handle Tables
        #     # Check for HTML content first
        #     if "text_as_html" in chunk.metadata:
        #         chunk.page_content = html_to_markdown(chunk.metadata["text_as_html"])
        #     else:
        #         # Fallback: If table has no HTML structure, just clean the text
        #         chunk.page_content = __TEXT_CLEANER.clean_chunk_text(chunk.page_content)
        
        # if category != "text" and "text_as_html" in chunk.metadata:
        #     chunk.page_content = html_to_markdown(chunk.metadata["text_as_html"])
        #     # markdown = html_to_markdown(chunk.metadata["text_as_html"])
        # else:
        #     # STRATEGY B: Handle Text/Titles
        #     # Apply your sophisticated TextCleaner logic here
        #     chunk.page_content = __TEXT_CLEANER.clean_chunk_text(chunk.page_content)
        
        # print("\n\n\n\n\n", chunk.page_content, "\n\n\n\n\n")
        
        
    # for chunk in chunks:
    #     # 1. Page Metadata
    #     current_page = chunk.metadata.get("page_number", 1)
    #     chunk.metadata["page"] = current_page
    #     if current_page > max_page:
    #         max_page = current_page

    #     # 2. Extract and Format Content
    #     # We check for 'orig_elements' to rebuild the chunk correctly.
    #     # This handles the 'CompositeElement' issue where headers and tables are mixed.
    #     orig_elements = chunk.metadata.get("orig_elements")
        
    #     if isinstance(orig_elements, list):
    #         new_content_parts = []
    #         for elem in orig_elements:

    #             print("\n\n\n\n\n", elem)
    #             # Safely handle if elem is a dict (standard for LangChain) or an object
    #             is_dict = isinstance(elem, dict)
                
    #             # Extract category and metadata safely
    #             category = elem.get("type") if is_dict else getattr(elem, "category", None)
    #             el_metadata = elem.get("metadata", {}) if is_dict else getattr(elem, "metadata", {})
    #             el_text = elem.get("text", "") if is_dict else getattr(elem, "text", "")

    #             if category == "Table" and "text_as_html" in el_metadata:
    #                 # Convert this specific part to Markdown
    #                 markdown_table = html_to_markdown(el_metadata["text_as_html"])
    #                 new_content_parts.append(markdown_table)
    #             else:
    #                 # Clean the plain text part
    #                 cleaned_text = __TEXT_CLEANER.clean_chunk_text(el_text)
    #                 if cleaned_text:
    #                     new_content_parts.append(cleaned_text)
            
    #         # Re-join the parts. Markdown tables need clear double-newlines to render.
    #         chunk.page_content = "\n\n".join(new_content_parts)

    #     # Fallback: If no orig_elements, but the top-level chunk is a Table
    #     elif chunk.metadata.get("category") == "Table" and "text_as_html" in chunk.metadata:
    #         chunk.page_content = html_to_markdown(chunk.metadata["text_as_html"])
        
    #     else:
    #         # Fallback: Just clean the existing page_content
    #         chunk.page_content = __TEXT_CLEANER.clean_chunk_text(chunk.page_content)

    # return chunks, max_page
    for chunk in chunks:
        current_page = chunk.metadata.get("page_number", 1)
        chunk.metadata["page"] = current_page
        max_page = max(max_page, current_page)

        # 1. Check for compressed 'orig_elements'
        orig_elements_raw = chunk.metadata.get("orig_elements")
        print(orig_elements_raw)
        
        if isinstance(orig_elements_raw, str) and len(orig_elements_raw) > 0:
            print("\n\n\n\n\n\n1111111\n\n\n\n\n")
            try:
                # DECOMPRESS: Unstructured uses Gzip + Base64 for serialization
                decoded_bytes = base64.b64decode(orig_elements_raw)
                decompressed_bytes = zlib.decompress(decoded_bytes)
                elements_list = json.loads(decompressed_bytes)
                
                reconstructed_parts = []
                for el in elements_list:
                    # 'el' is now a dictionary
                    category = el.get("type")
                    text = el.get("text", "")
                    el_metadata = el.get("metadata", {})
                    
                    if category == "Table" and "text_as_html" in el_metadata:
                        # Convert table to markdown
                        reconstructed_parts.append(html_to_markdown(el_metadata["text_as_html"]))
                    else:
                        # Clean normal text lines using your TextCleaner
                        cleaned_text = __TEXT_CLEANER.clean_chunk_text(text)
                        if cleaned_text:
                            reconstructed_parts.append(cleaned_text)
                
                chunk.page_content = "\n\n".join(reconstructed_parts)
                print(chunk.page_content)
                continue # Move to next chunk
                
            except Exception as e:
                print("\n\n\n\n\n\n-----------------\n\n\n\n\n")
                print(f"Decompression failed: {e}")
                # If decompression fails, we fall through to standard cleaning

        # 2. Fallback: Top-level Table check
        if chunk.metadata.get("category") == "Table" and "text_as_html" in chunk.metadata:
            print("\n\n\n\n\n\n222222\n\n\n\n\n")
            chunk.page_content = html_to_markdown(chunk.metadata["text_as_html"])
        else:
            # 3. Fallback: Standard text cleaning
            print("\n\n\n\n\n\n333333\n\n\n\n\n")
            chunk.page_content = __TEXT_CLEANER.clean_chunk_text(chunk.page_content)
            print(chunk.page_content)

    return chunks, max_page


async def embed_chunks(raw_chunks: list[Document]) -> list[list[float]]:
    contents = []
    for chunk in raw_chunks:
        category = chunk.metadata.get("category", "text")
        page = chunk.metadata.get("page", "?")
        
        # Help the LLM identify tables during retrieval
        prefix = f"[Source: Page {page}, Type: {category}]"
        contents.append(f"{prefix}\n{chunk.page_content}")
        
    return await EMBEDDING_CLIENT.aembed_documents(contents)

# async def embed_chunks(raw_chunks: list[Document]) -> list[list[float]]:
#     """Create embedding vectors for the raw chunks.

#     Args:
#         raw_chunks (list[Document]): List of raw chunks from the PDF.

#     Returns:
#         list[list[float]]: List of embedding vectors for each chunk.
#     """
#     contents = [
#         # chunk.page_content
#         f"title: {chunk.metadata.get('title', 'none')} | text: {chunk.page_content}"
#         for chunk in raw_chunks
#     ]
#     return await EMBEDDING_CLIENT.aembed_documents(contents)


# async def similarity_search(
#     query: str,
#     user_id: PydanticObjectId,
#     # resource_ids: list[PydanticObjectId] | None,
#     resource_ids: Optional[List[PydanticObjectId]]
# # ) -> list[PDFChunk | Chunk]:
# ) -> list[Union[PDFChunk, Chunk]]:
#     """Perform a similarity search for the given query.

#     Args:
#         query (str): The query string to search for.
#         user_id (PydanticObjectId): The ID of the user making the request.
#         resource_ids (list[PydanticObjectId]): List of resource IDs to search within. (Optional)

#     Returns:
#         list[Chunk]: List of chunks that match the query.
#     """
#     formatted_query = f"task: search result | query:{query}"
#     query_embedding = await EMBEDDING_CLIENT.aembed_query(formatted_query)

#     pre_filter = {"user": user_id}

#     if resource_ids:
#         pre_filter["resource"] = {"$in": resource_ids}

#     search_stage = vector_search_stage(
#         query_embedding,
#         CONFIG.mongo.search_index_field,
#         CONFIG.mongo.search_index_name,
#         CONFIG.mongo.search_top_k,
#         pre_filter,
#     )

#     pipeline = [search_stage]
#     # collection = Chunk.get_motor_collection()
#     collection = Chunk.get_pymongo_collection()

#     results = await collection.aggregate(pipeline).to_list()

#     # chunks = []
#     # for result in results:
#     #     if "page_number" in result:
#     #         chunks.append(PDFChunk(**result))
#     #     else:
#     #         chunks.append(Chunk(**result))

#     # return chunks

#     # results = await collection.aggregate(pipeline).to_list()

#     # Build vectors and apply threshold
#     indexed = [
#         (idx, r)
#         for idx, r in enumerate(results)
#         if isinstance(r.get("embedding"), list)
#     ]
#     if not indexed:
#         return []

#     doc_vecs = [r["embedding"] for _, r in indexed]
#     relevances = [__MMR_SELECTOR._cosine(query_embedding, v) for v in doc_vecs]

#     # Filter by similarity threshold
#     filtered = [
#         (i, r, s)
#         for (i, r), s in zip(indexed, relevances)
#         if s >= CONFIG.embedding_client.mmr_similarity_threashold
#     ]
#     if not filtered:
#         return []

#     filtered_doc_vecs = [r["embedding"] for _, r, _ in filtered]
#     selected_rel_indices = __MMR_SELECTOR.select(
#         query_embedding,
#         filtered_doc_vecs,
#     )

#     # Map back to original results order
#     selected = [filtered[i] for i in selected_rel_indices]

#     # chunks: list[Union[PDFChunk, Chunk]] = []
#     # for _, result, _ in selected:
#     #     if "page_number" in result:
#     #         chunks.append(PDFChunk(**result))
#     #     else:
#     #         chunks.append(Chunk(**result))

#     chunks = []
#     for result in results:
#         # Convert MongoDB's _id to id if needed
#         if '_id' in result and 'id' not in result:
#             result['id'] = result.pop('_id')
        
#         try:
#             if "page_number" in result:
#                 chunks.append(PDFChunk(**result))
#             else:
#                 chunks.append(Chunk(**result))
#         except Exception as e:
#             print(f"Error creating chunk: {e}")
#             continue


#     return chunks

async def similarity_search(
    query: str,
    user_id: PydanticObjectId,
    resource_ids: Optional[List[PydanticObjectId]]
) -> list[Union[PDFChunk, Chunk]]:
    """Perform a similarity search for the given query."""
    formatted_query = f"task: search result | query: {query}"
    query_embedding = await EMBEDDING_CLIENT.aembed_query(formatted_query)

    pre_filter = {"user": user_id}
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

    collection = Chunk.get_pymongo_collection()
    results = await collection.aggregate(pipeline).to_list()

    # Prepare vectors for MMR
    indexed = [
        (idx, r)
        for idx, r in enumerate(results)
        if isinstance(r.get("embedding"), list)
    ]
    if not indexed:
        return []

    doc_vecs = [r["embedding"] for _, r in indexed]

    # Compute cosine similarities and threshold
    relevances = [__MMR_SELECTOR._cosine(query_embedding, v) for v in doc_vecs]
    filtered = [
        (i, r, s)
        for (i, r), s in zip(indexed, relevances)
        if s >= CONFIG.embedding_client.mmr_similarity_threashold
    ]
    if not filtered:
        return []

    # Run MMR on filtered docs
    filtered_doc_vecs = [r["embedding"] for _, r, _ in filtered]
    selected_rel_indices = __MMR_SELECTOR.select(query_embedding, filtered_doc_vecs)
    if not selected_rel_indices:
        return []

    # Build chunks only from the MMR-selected docs (in selected order)
    chunks: list[Union[PDFChunk, Chunk]] = []
    for sel_idx in selected_rel_indices:
        _, result, _ = filtered[sel_idx]

        # Normalize id field if needed
        if "_id" in result and "id" not in result:
            result["id"] = result.pop("_id")

        try:
            if "page_number" in result:
                chunks.append(PDFChunk(**result))
            else:
                chunks.append(Chunk(**result))
        except Exception as e:
            print(f"Error creating chunk: {e}")
            continue

    return chunks