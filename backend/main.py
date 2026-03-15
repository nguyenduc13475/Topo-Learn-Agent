from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from app.db.postgres import engine, Base

# Create all database tables based on SQLAlchemy models
print("Initializing Database Tables...")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for Intelligent Learning Systems using Knowledge Graph & AI",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Welcome to Topo-Learn-Agent API. The server is up and running!"}
