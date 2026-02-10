from typing import Dict, List, Any
from fastapi import WebSocket
import json
import logging
import asyncio
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # In-memory connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Match groups: match_id -> List[user_id]
        self.match_connections: Dict[str, List[str]] = {}
        # User to Match mapping: user_id -> match_id
        self.user_to_match: Dict[str, str] = {}
        
        # Redis connection for pub/sub (scaling)
        self.redis = redis.from_url(f"redis://{settings.REDIS_HOST}:6379", decode_responses=True)

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")
        
        # Remove from match mapping if any
        if user_id in self.user_to_match:
            match_id = self.user_to_match[user_id]
            if match_id in self.match_connections:
                if user_id in self.match_connections[match_id]:
                    self.match_connections[match_id].remove(user_id)
                if not self.match_connections[match_id]:
                    del self.match_connections[match_id]
            del self.user_to_match[user_id]

    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                self.disconnect(user_id)

    async def broadcast_to_match(self, match_id: str, message: Dict[str, Any]):
        """Broadcast message to all users in a specific match"""
        # In a scaled environment, this would publish to Redis channel
        # For now, we iterate through local connections if we know who is in the match
        # Ideally, we should track match participants in memory or Redis
        
        # We need a way to know which users are in a match. 
        # The manager needs to be told when a match starts or users join.
        pass

    async def add_user_to_match(self, match_id: str, user_id: str):
        if match_id not in self.match_connections:
            self.match_connections[match_id] = []
        if user_id not in self.match_connections[match_id]:
            self.match_connections[match_id].append(user_id)
        self.user_to_match[user_id] = match_id

    async def remove_user_from_match(self, match_id: str, user_id: str):
        if user_id in self.user_to_match:
            del self.user_to_match[user_id]
            
        if match_id in self.match_connections:
            if user_id in self.match_connections[match_id]:
                self.match_connections[match_id].remove(user_id)
            if not self.match_connections[match_id]:
                del self.match_connections[match_id]

    async def broadcast_match_event(self, match_id: str, event_type: str, data: Dict[str, Any]):
        message = {"event": event_type, "data": data}
        
        if match_id in self.match_connections:
            for user_id in self.match_connections[match_id]:
                await self.send_personal_message(message, user_id)

manager = ConnectionManager()
