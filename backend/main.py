import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.router import api_router
from app.api.v1.ws import router as ws_router
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.neo4j import neo4j_conn
from app.db.postgres import Base, engine
from app.services.ws_manager import ws_manager

# Create all database tables
print("[Main] Initializing Database Tables...")
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Main] Starting up resources...")
    # Initialize Neo4j constraints to prevent graph duplication
    neo4j_conn.initialize_constraints()

    task = asyncio.create_task(ws_manager.listen_to_redis())
    yield
    print("[Main] Shutting down resources gracefully...")
    task.cancel()
    neo4j_conn.close()  # Clean up graph connections
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend for Intelligent Learning Systems using Knowledge Graph & AI",
    lifespan=lifespan,
)

# Mount static files directory for local storage fallback
os.makedirs("data/uploads/served", exist_ok=True)
app.mount(
    "/api/v1/static/uploads",
    StaticFiles(directory="data/uploads/served"),
    name="static_uploads",
)

# Apply Rate Limiting globally to protect backend from abuse in Alpha
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Allow dynamic origins for production, preventing whitespace issues
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router, prefix="/api/v1/ws", tags=["WebSocket"])
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Welcome to Topo-Learn-Agent API. The server is up and running!"}
