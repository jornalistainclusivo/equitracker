from fastapi import APIRouter
from app.api.v1.endpoints import sources, chat

api_router = APIRouter()
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
