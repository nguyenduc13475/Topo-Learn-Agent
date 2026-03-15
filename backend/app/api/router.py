from fastapi import APIRouter
from app.api.v1 import document, graph, quiz, review, auth

api_router = APIRouter()

# Include all sub-routers with their specific prefixes and tags
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz & Tutor"])
api_router.include_router(
    review.router, prefix="/review", tags=["Spaced Repetition (SM-2)"]
)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
