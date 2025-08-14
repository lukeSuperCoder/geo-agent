"""
WebSocket API处理模块
支持流式聊天和地图联动
"""
import json
import uuid
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.message import UserMessage, MessageType
from app.services.chat_service import chat_service
from app.services.stream_chat_service import stream_chat_service


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
                
                # 处理不同类型的消息
                message_type = message_data.get("type", "")
                
                if message_type == "chat":
                    # 流式聊天消息
                    await handle_stream_chat(websocket, message_data, session_id)
                    
                elif message_type == "user_input":
                    # 传统意图解析消息
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


async def handle_stream_chat(websocket: WebSocket, message_data: dict, session_id: str):
    """处理流式聊天消息"""
    try:
        message = message_data.get("message", "")
        if not message:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": "消息内容不能为空",
                "session_id": session_id
            }))
            return
        
        # 调用流式聊天服务
        async for response in stream_chat_service.stream_chat(message, session_id):
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        logger.error(f"流式聊天处理失败: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": f"聊天服务出错: {str(e)}",
            "session_id": session_id
        })) 