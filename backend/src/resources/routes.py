from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from src.auth.dependencies import current_user
import src.resources.database as resources_db
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
