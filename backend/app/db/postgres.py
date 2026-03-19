from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Production-grade connection pooling for 1000 users Scaled down per-worker to
# stay strictly within PostgreSQL's default 100 max_connections
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,  # 10 * 4 workers = 40 baseline connections
    max_overflow=10,  # Max 80 connections across all workers during spikes
    pool_timeout=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
