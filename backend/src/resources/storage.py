import os

from beanie import PydanticObjectId
from fastapi import UploadFile

from src.config import CONFIG
from src.resources.models import ResourceType


async def store_resource_file(
    file: UploadFile,
    user_id: PydanticObjectId,
    resource_type: ResourceType,
    resource_id: PydanticObjectId,
) -> str:
    """Store a resource file in the storage system.

    Args:
        file (UploadFile): The file to be stored.
        user_id (PydanticObjectId): The ID of the user who owns the resource.
        resource_type (ResourceType): The type of the resource.
        resource_id (PydanticObjectId): The ID of the resource.

    Returns:
        str: The storage path of the stored file.
    """
    storage_path = os.path.join(
        CONFIG.storage.directory,
        str(user_id),
        resource_type.value,
        str(resource_id),
    )

    if resource_type == ResourceType.PDF:
        storage_path += ".pdf"

    elif resource_type == ResourceType.WEBPAGE:
        storage_path += ".html"

    with open(storage_path, "wb") as f:
        f.write(await file.read())

    return storage_path
