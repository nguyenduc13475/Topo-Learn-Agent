import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import settings
from app.db.neo4j import neo4j_conn

router = APIRouter()


@router.get("/")
def check_health(db: Session = Depends(get_db)):
    """Deep health check of all connected services."""
    health_status = {"status": "healthy", "services": {}}

    # Check Postgres
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "up"
    except Exception:
        health_status["services"]["postgres"] = "down"
        health_status["status"] = "unhealthy"

    # Check Neo4j
    try:
        with neo4j_conn.get_session() as session:
            session.run("RETURN 1")
        health_status["services"]["neo4j"] = "up"
    except Exception:
        health_status["services"]["neo4j"] = "down"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        with redis.from_url(settings.CELERY_BROKER_URL) as r:
            r.ping()
        health_status["services"]["redis"] = "up"
    except Exception:
        health_status["services"]["redis"] = "down"
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status
