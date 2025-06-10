from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from src.auth.dependencies import current_user
from src.chat.models import ResourceChatBody
from src.nlp.chat import stream_response, clear_chat
from src.nlp.embeddings import similarity_search
from src.users.models import UserDB


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(
    body: ResourceChatBody, user: Annotated[UserDB, Depends(current_user)]
) -> StreamingResponse:
    """Chat with resources based on the provided query and resource IDs.

    Args:
        body (ResourceChatBody): The request body containing the query and resource IDs.
        user (UserDB): The authenticated user making the request.

    Returns:
        StreamingResponse: A streaming response containing the chat model's response.

    Raises:
        HTTPException: If no resources are found for the given user or resource IDs.
    """
    chunks = await similarity_search(
        query=body.query,
        user_id=user.id,
        resource_ids=body.resource_ids,
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resources found for the given user or resource IDs.",
        )

    return StreamingResponse(
        content=stream_response(body.query, chunks, user.id),
        media_type="text/event-stream",
    )


@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear(user: Annotated[UserDB, Depends(current_user)]) -> None:
    """Clear the chat history for the authenticated user.

    Args:
        user (UserDB): The authenticated user making the request.
    """
    clear_chat(user.id)
