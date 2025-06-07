import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.operations import SearchIndexModel
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from src.config import CONFIG
from src.resources.models import (
    Chunk,
    Resource,
    PDFResource,
    WebpageResource,
    PDFChunk,
    WebpageChunk,
)
from src.users.models import UserDB
from src.users.routes import router as UsersRouter
from src.auth.routes import router as AuthRouter
from src.resources.routes import router as ResourcesRouter
from src.chat.routes import router as ChatRouter


logging.basicConfig(level=logging.INFO)
__logger = logging.getLogger(__name__)


TITLE = """doc-rag API"""
DESCRIPTION = """This API powers doc-rag."""

DOCUMENT_MODELS = [
    UserDB,
    Resource,
    PDFResource,
    WebpageResource,
    Chunk,
    PDFChunk,
    WebpageChunk,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes application services."""

    app.mongodb_client = AsyncIOMotorClient(CONFIG.mongo.uri)
    app.db = app.mongodb_client.get_database(CONFIG.mongo.db_name)

    try:
        ping_response = await app.db.command("ping")
    except ServerSelectionTimeoutError:
        raise Exception("Timeout while connecting to MongoDB.")

    if int(ping_response["ok"]) != 1:
        raise Exception("Could not connect to MongoDB.")

    __logger.info("MongoDB connection initialized successfully")

    await init_beanie(app.db, document_models=DOCUMENT_MODELS)
    __logger.info("Beanie initialized successfully")

    collection = app.db.get_collection("chunks")
    search_index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": CONFIG.mongo.search_index_dimensions,
                    "path": CONFIG.mongo.search_index_field,
                    "similarity": CONFIG.mongo.search_index_similarity,
                }
            ]
        },
        name=CONFIG.mongo.search_index_name,
        type="vectorSearch",
    )
    await collection.create_search_index(search_index_model)
    __logger.info("Search index created successfully")

    yield

    app.mongodb_client.close()
    __logger.info("MongoDB connection closed")


app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=CONFIG.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CONFIG.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter)
app.include_router(UsersRouter)
app.include_router(ResourcesRouter)
app.include_router(ChatRouter)
