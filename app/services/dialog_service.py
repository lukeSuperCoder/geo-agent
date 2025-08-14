"""
对话服务 - 直接调用Qwen API进行流式对话
使用OpenAI兼容模式
"""
import os
import json
from typing import AsyncGenerator
from openai import OpenAI
from loguru import logger

from app.config import settings


class DialogService:
    """对话服务"""
    
    def __init__(self):
        self.api_key = settings.qwen_api_key
        self.model = settings.qwen_model
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """流式对话"""
        try:
            logger.info(f"开始流式对话: {user_input}")
            
            # 构建对话消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个友好的地理信息助手，请用自然、流畅的语言回答用户的问题。"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            
            # 调用Qwen API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000,
                # Qwen3模型通过enable_thinking参数控制思考过程
                # extra_body={"enable_thinking": False}
            )
            
            # 处理流式响应
            for chunk in completion:
                # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                        
        except Exception as e:
            logger.error(f"流式对话失败: {str(e)}")
            yield f"抱歉，处理您的请求时出现了错误: {str(e)}"
    
    async def chat_simple(self, user_input: str) -> str:
        """简单对话（非流式）"""
        try:
            logger.info(f"开始简单对话: {user_input}")
            
            # 构建对话消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个友好的地理信息助手，请用自然、流畅的语言回答用户的问题。"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            
            # 调用Qwen API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=1000
            )
            
            return completion.choices[0].message.content
                
        except Exception as e:
            logger.error(f"简单对话失败: {str(e)}")
            return f"抱歉，处理您的请求时出现了错误: {str(e)}"


# 全局对话服务实例
dialog_service = DialogService() 