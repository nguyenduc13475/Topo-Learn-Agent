from fastapi import APIRouter

from app.api.v1 import auth, dashboard, document, graph, health, quiz, review

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz & Tutor"])
api_router.include_router(
    review.router, prefix="/review", tags=["Spaced Repetition (SM-2)"]
)
