"""
WebSocket manager for real-time progress updates
Uses Redis pub/sub for multi-worker support
"""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket
from redis import Redis
from ..config import settings
import asyncio

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and Redis pub/sub for progress updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client: Redis = None
        self.pubsub = None
        self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis connection for pub/sub"""
        try:
            from ..services.queue import get_redis_connection
            self.redis_client = get_redis_connection()
            self.pubsub = self.redis_client.pubsub()
            logger.info("WebSocket manager connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available for WebSocket: {e}")
            self.redis_client = None
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Connect a WebSocket to a channel"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Disconnect a WebSocket from a channel"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info(f"WebSocket disconnected from channel: {channel}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast a message to all WebSockets in a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections[channel]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            self.disconnect(ws, channel)
    
    def publish_progress(self, channel: str, data: dict):
        """Publish progress update to Redis (for multi-worker support)"""
        if self.redis_client:
            try:
                message = json.dumps(data)
                self.redis_client.publish(f"batch_progress:{channel}", message)
            except Exception as e:
                logger.error(f"Error publishing to Redis: {e}")
    
    async def listen_to_redis(self):
        """Listen to Redis pub/sub and broadcast to WebSocket channels"""
        if not self.redis_client or not self.pubsub:
            return
        
        # Subscribe to all batch progress channels
        self.pubsub.psubscribe("batch_progress:*")
        
        try:
            while True:
                message = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    channel_pattern = message['channel'].decode('utf-8')
                    # Extract batch_id from channel: batch_progress:job_id:batch_id
                    parts = channel_pattern.split(':')
                    if len(parts) >= 3:
                        batch_id = parts[-1]
                        job_id = parts[-2] if len(parts) >= 3 else None
                        channel = f"{job_id}:{batch_id}" if job_id else batch_id
                        
                        try:
                            data = json.loads(message['data'])
                            await self.broadcast_to_channel(channel, data)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in Redis message: {message['data']}")
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")


# Global WebSocket manager instance
manager = WebSocketManager()
