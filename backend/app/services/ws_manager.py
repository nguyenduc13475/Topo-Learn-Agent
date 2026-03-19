import asyncio
import contextlib
import json
from typing import Dict, List

import redis.asyncio as redis
from fastapi import WebSocket

from app.core.config import settings


class WebSocketManager:
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"[WebSocket] User {user_id} connected.")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"[WebSocket] User {user_id} disconnected.")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            disconnected_sockets = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"[WebSocket] Error sending to user {user_id}: {e}")
                    disconnected_sockets.append(connection)

            # Cleanup dead connections
            for conn in disconnected_sockets:
                self.disconnect(conn, user_id)

    async def listen_to_redis(self):
        """Run a background task in FastAPI to capture events from the Celery worker."""
        print("[Redis PubSub] Starting listener...")

        while True:
            try:
                # ADDED health_check_interval to prevent silent connection drops
                self.redis_client = redis.from_url(
                    settings.CELERY_BROKER_URL, health_check_interval=30
                )
                self.pubsub = self.redis_client.pubsub()
                await self.pubsub.subscribe("user_notifications")

                print("[Redis PubSub] Successfully connected and listening.")
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        target_user = data.get("user_id")
                        if target_user:
                            await self.send_personal_message(data, target_user)
            except asyncio.CancelledError:
                print("[Redis PubSub] Listener gracefully stopped.")
                break
            except Exception as e:
                print(
                    f"[Redis PubSub] Connection dropped: {e}. Reconnecting in 5 seconds..."
                )
                await asyncio.sleep(5)
            finally:
                # ADDED safe cleanup to prevent connection leaks on the Redis server
                if self.pubsub:
                    with contextlib.suppress(Exception):
                        await self.pubsub.unsubscribe("user_notifications")
                if self.redis_client:
                    with contextlib.suppress(Exception):
                        await self.redis_client.close()


ws_manager = WebSocketManager()
