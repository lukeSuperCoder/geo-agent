"""
聊天API模块 - 提供HTTP接口直接调用OpenAI API
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import json
import uuid
from loguru import logger

from app.services.stream_chat_service import stream_chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message_id: str
    session_id: str
    content: str
    status: str


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """流式聊天接口 - 真正的流式输出"""
    try:
        # 生成消息ID
        message_id = str(uuid.uuid4())
        session_id = request.session_id or str(uuid.uuid4())
        
        async def generate_stream() -> AsyncGenerator[str, None]:
            """生成流式响应"""
            try:
                # 发送流式开始消息
                start_data = {
                    "type": "stream_start", 
                    "message_id": message_id, 
                    "session_id": session_id
                }
                yield f"data: {json.dumps(start_data, ensure_ascii=False)}\n\n"
                
                # 调用流式聊天服务
                chunk_count = 0
                async for response in stream_chat_service.stream_chat(
                    request.message, 
                    session_id
                ):
                    if response["type"] == "stream_chunk":
                        chunk_count += 1
                        # 发送内容片段 - 真正的流式输出
                        chunk_data = {
                            "type": "stream_chunk", 
                            "message_id": message_id, 
                            "chunk": response["chunk"]
                        }
                        chunk_str = f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                        yield chunk_str
                        
                        # 调试信息
                        if chunk_count % 10 == 0:
                            logger.debug(f"已发送 {chunk_count} 个字符片段")
                        
                    elif response["type"] == "stream_end":
                        # 发送结束消息
                        end_data = {
                            "type": "stream_end", 
                            "message_id": message_id, 
                            "session_id": session_id
                        }
                        yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"
                        logger.info(f"流式输出完成，总共发送 {chunk_count} 个字符片段")
                        break
                        
                    elif response["type"] == "error":
                        # 发送错误消息
                        error_data = {
                            "type": "error", 
                            "message_id": message_id, 
                            "error": response["error"]
                        }
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"流式生成失败: {str(e)}")
                error_data = {
                    "type": "error", 
                    "message_id": message_id, 
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*",
                "X-Accel-Buffering": "no",  # 禁用nginx缓冲
                "Transfer-Encoding": "chunked"
            }
        )
        
    except Exception as e:
        logger.error(f"聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天服务出错: {str(e)}")


@router.post("/")
async def chat(request: ChatRequest):
    """普通聊天接口（非流式）"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # 收集完整的响应内容
        full_content = ""
        async for response in stream_chat_service.stream_chat(request.message, session_id):
            if response["type"] == "stream_chunk":
                full_content += response["chunk"]
            elif response["type"] == "error":
                raise HTTPException(status_code=500, detail=response["error"])
        
        return ChatResponse(
            message_id=message_id,
            session_id=session_id,
            content=full_content,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天服务出错: {str(e)}")


@router.get("/health")
async def chat_health():
    """聊天服务健康检查"""
    return {
        "status": "healthy",
        "service": "chat-api",
        "provider": "qwen"  # 可以根据配置动态返回
    } 