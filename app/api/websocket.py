"""
WebSocket API处理模块
"""
import json
import uuid
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.message import UserMessage, MessageType
from app.services.chat_service import chat_service


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        logger.info(f"WebSocket连接建立: {connection_id}, 会话: {session_id}")
    
    def disconnect(self, connection_id: str, session_id: str):
        """断开WebSocket连接"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"WebSocket连接断开: {connection_id}, 会话: {session_id}")
    
    async def send_message(self, connection_id: str, message: dict):
        """发送消息到指定连接"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"发送消息失败: {str(e)}")
                self.disconnect(connection_id, "")
    
    async def send_to_session(self, session_id: str, message: dict):
        """发送消息到会话的所有连接"""
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id].copy():
                await self.send_message(connection_id, message)


# 全局WebSocket管理器
websocket_manager = WebSocketManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str = None):
    """WebSocket端点处理函数"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    await websocket_manager.connect(websocket, session_id)
    connection_id = None
    
    try:
        # 发送连接成功消息
        await websocket.send_text(json.dumps({
            "type": "system",
            "message": "连接成功",
            "session_id": session_id
        }))
        
        # 处理消息
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 找到当前连接ID
                for cid, ws in websocket_manager.active_connections.items():
                    if ws == websocket:
                        connection_id = cid
                        break
                
                # 处理用户消息
                if message_data.get("type") == "user_input":
                    user_message = UserMessage(
                        message=message_data["message"],
                        session_id=session_id
                    )
                    
                    # 处理消息并发送响应
                    responses = await chat_service.process_message(user_message)
                    for response in responses:
                        await websocket_manager.send_message(connection_id, response)
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "消息格式错误",
                    "session_id": session_id
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket处理错误: {str(e)}")
    finally:
        if connection_id:
            websocket_manager.disconnect(connection_id, session_id) 