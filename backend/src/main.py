import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo.errors import ServerSelectionTimeoutError
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from src.config import CONFIG
from src.nlp.embeddings import create_search_index
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

from src.resources.models import Chunk


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
    
    await create_search_index()
    __logger.info("Search index created successfully")

    yield

    app.mongodb_client.close()
    __logger.info("MongoDB connection closed")


app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter)
app.include_router(UsersRouter)
app.include_router(ResourcesRouter)
app.include_router(ChatRouter)
