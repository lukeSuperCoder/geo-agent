"""
流式聊天服务 - 支持实时流式输出
"""
import json
import uuid
from typing import AsyncGenerator, Dict, Any
from openai import OpenAI
from loguru import logger

from app.config import settings


class StreamChatService:
    """流式聊天服务"""
    
    def __init__(self):
        self.client = self._init_client()
    
    def _init_client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        if settings.ai_provider.lower() == "qwen":
            if not settings.qwen_api_key:
                raise ValueError("Qwen API Key未配置")
            
            return OpenAI(
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        elif settings.ai_provider.lower() == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API Key未配置")
            
            return OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )
        else:
            raise ValueError(f"不支持的AI提供商: {settings.ai_provider}")
    
    def _get_model(self) -> str:
        """获取模型名称"""
        if settings.ai_provider.lower() == "qwen":
            return settings.qwen_model
        elif settings.ai_provider.lower() == "openai":
            return settings.openai_model
        else:
            return "gpt-4o-mini"  # 默认模型
    
    async def stream_chat(self, message: str, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天接口 - 真正的流式输出"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        message_id = str(uuid.uuid4())
        
        try:
            # 发送流式开始消息
            yield {
                "type": "stream_start",
                "message_id": message_id,
                "session_id": session_id
            }
            
            # 构建对话历史
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的地理信息助手Geo-Agent，具有以下能力：
1. 天气查询：可以查询全国各地的天气信息
2. POI搜索：可以搜索兴趣点，如餐厅、酒店、景点等
3. 地理建议：提供地理相关的建议和信息
4. 地图操作：支持地图飞行、标记点等操作

请用友好、专业的语气回答用户问题。如果用户询问地理相关信息，请提供准确、有用的回答。
如果涉及天气或POI查询，请说明你可以通过插件获取实时数据。"""
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
            
            logger.info(f"开始调用流式API，消息: {message[:50]}...")
            
            # 调用真正的流式API
            stream = self.client.chat.completions.create(
                model=self._get_model(),
                messages=messages,
                stream=True,  # 启用真正的流式输出
                temperature=0.7,
                max_tokens=1000
            )
            
            # 直接处理流式响应，不添加人为延迟
            chunk_count = 0
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    chunk_count += 1
                    
                    # 立即发送每个字符片段，这是真正的流式
                    yield {
                        "type": "stream_chunk",
                        "message_id": message_id,
                        "chunk": content,
                        "session_id": session_id
                    }
                    
                    # 调试信息
                    if chunk_count % 20 == 0:
                        logger.debug(f"已处理 {chunk_count} 个字符片段")
            
            logger.info(f"流式API调用完成，总共处理 {chunk_count} 个字符片段")
            
            # 发送流式结束消息
            yield {
                "type": "stream_end",
                "message_id": message_id,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            yield {
                "type": "error",
                "message_id": message_id,
                "error": f"聊天服务出错: {str(e)}",
                "session_id": session_id
            }


# 全局流式聊天服务实例
stream_chat_service = StreamChatService() 