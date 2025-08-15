"""
流式聊天服务 - 支持实时流式输出和意图解析
使用阿里云百炼API进行自然语言对话
"""
import json
import uuid
import os
from typing import AsyncGenerator, Dict, Any
from openai import OpenAI
from loguru import logger

from app.config import settings


class StreamChatService:
    """流式聊天服务"""
    
    def __init__(self):
        if not settings.dashscope_api_key:
            raise ValueError("阿里云百炼API Key未配置")
        
        self.client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url
        )
        self.model = settings.dashscope_model
        logger.info(f"初始化流式聊天服务，使用阿里云百炼模型: {self.model}")
        
        # 预定义示例响应（用于few-shot提示）
        example1_response = json.dumps(
            {
                "intent": "weather_query",
                "confidence": 0.95,
                "parameters": {
                    "location": "北京",
                    "query_type": "天气"
                }
            },
            ensure_ascii=False
        )
        
        example2_response = json.dumps(
            {
                "intent": "poi_search",
                "confidence": 0.92,
                "parameters": {
                    "location": "附近",
                    "keyword": "餐厅",
                    "query_type": "POI搜索"
                }
            },
            ensure_ascii=False
        )
        
        example3_response = json.dumps(
            {
                "intent": "route_planning",
                "confidence": 0.88,
                "parameters": {
                    "start_location": "北京",
                    "end_location": "上海",
                    "query_type": "路径规划"
                }
            },
            ensure_ascii=False
        )
        
        example4_response = json.dumps(
            {
                "intent": "map_fly_to",
                "confidence": 0.90,
                "parameters": {
                    "location": "上海",
                    "query_type": "地图飞行"
                }
            },
            ensure_ascii=False
        )
        
        # 意图解析的Prompt模板（使用few-shot示例）
        self.intent_system_prompt = f"""你是一个地理信息助手，负责理解用户的自然语言输入并解析出意图。

提取intent、confidence和parameters，输出JSON格式的解析结果。

支持的意图类型：
- weather_query: 天气查询
- poi_search: 兴趣点搜索
- route_planning: 路径规划
- map_fly_to: 地图飞行到指定位置
- location_search: 地点搜索
- unknown: 未知意图

示例：
Q：我想看看北京的天气
A：{example1_response}

Q：搜索附近的餐厅
A：{example2_response}

Q：从北京到上海的路线
A：{example3_response}

Q：飞到上海
A：{example4_response}"""
    
    async def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """解析用户意图"""
        try:
            logger.info(f"开始解析用户意图: {user_input}")
            
            # 调用AI模型进行意图解析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.intent_system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            intent_data = json.loads(response.choices[0].message.content)
            
            logger.info(f"意图解析成功: {intent_data.get('intent', 'unknown')}, 置信度: {intent_data.get('confidence', 0.0)}, 参数: {intent_data.get('parameters', {})}")
            return intent_data
            
        except Exception as e:
            logger.error(f"意图解析失败: {str(e)}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "parameters": {},
                "error": str(e)
            }
    
    async def stream_chat(self, message: str, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天接口"""
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
            
            # 首先进行意图解析
            intent_result = await self.parse_intent(message)
            
            # 发送意图解析结果
            yield {
                "type": "intent_parsed",
                "message_id": message_id,
                "intent": intent_result,
                "session_id": session_id
            }
            
            # 构建对话消息
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
            
            logger.info(f"开始流式对话，消息: {message[:50]}...")
            
            # 调用阿里云百炼API
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=1000
            )
            
            # 处理流式响应 - 使用同步迭代器但返回异步生成器
            chunk_count = 0
            try:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        chunk_count += 1
                        
                        # 发送每个字符片段
                        yield {
                            "type": "stream_chunk",
                            "message_id": message_id,
                            "chunk": content,
                            "session_id": session_id
                        }
                        # 添加小延迟确保流式效果
                        import asyncio
                        await asyncio.sleep(0.01)
                        
            except Exception as e:
                logger.error(f"流式处理失败: {str(e)}")
                yield {
                    "type": "error",
                    "message_id": message_id,
                    "error": f"流式处理失败: {str(e)}",
                    "session_id": session_id
                }
                return
            
            logger.info(f"流式对话完成，处理了 {chunk_count} 个字符片段")
            
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