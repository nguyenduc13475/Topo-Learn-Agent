import os

from celery import Celery
from celery.signals import worker_process_init

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "topo_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.services.ingestion_svc", "app.services.graph_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=3600,
    task_ignore_result=True,
)


@worker_process_init.connect
def init_worker(**kwargs):
    """
    Signal handler to cleanly reset DB connections right after the Celery worker
    process forks.
    """
    print("[Celery] Worker process initialized. Setting up resources...")

    from app.db.postgres import engine

    engine.dispose()
    print("[Celery] Postgres engine connection pool reset.")

    from app.core.config import settings
    from app.db.neo4j import neo4j_conn

    neo4j_conn.close()
    neo4j_conn.__init__(
        settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD
    )
    print("[Celery] Neo4j driver re-initialized.")
