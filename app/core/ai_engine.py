"""
AI引擎模块 - 负责意图解析和自然语言理解
"""
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from loguru import logger

from app.config import settings
from app.models.message import IntentResult, IntentType


class AIEngine:
    """AI意图解析引擎"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        # 意图解析的Prompt模板
        self.intent_prompt = """
你是一个地理信息助手，负责理解用户的自然语言输入并解析出意图。

请分析用户的输入，并返回JSON格式的解析结果：

{
    "intent": "意图类型",
    "confidence": 0.95,
    "parameters": {
        "location": "地点名称",
        "query_type": "查询类型",
        "other_params": "其他参数"
    }
}

支持的意图类型：
- weather_query: 天气查询
- poi_search: 兴趣点搜索
- route_planning: 路径规划
- map_fly_to: 地图飞行到指定位置
- location_search: 地点搜索
- unknown: 未知意图

用户输入: {user_input}

请返回JSON格式的解析结果：
"""

    async def parse_intent(self, user_input: str, session_id: str) -> IntentResult:
        """解析用户意图"""
        try:
            logger.info(f"开始解析用户意图: {user_input}")
            
            # 构建完整的Prompt
            full_prompt = self.intent_prompt.format(user_input=user_input)
            
            # 调用OpenAI API
            response = await self._call_openai(full_prompt)
            
            # 解析响应
            intent_data = self._parse_response(response)
            
            # 构建意图结果
            intent_result = IntentResult(
                intent=IntentType(intent_data.get("intent", "unknown")),
                confidence=float(intent_data.get("confidence", 0.0)),
                parameters=intent_data.get("parameters", {}),
                raw_text=user_input,
                session_id=session_id
            )
            
            logger.info(f"意图解析成功: {intent_result.intent}, 置信度: {intent_result.confidence}")
            return intent_result
            
        except Exception as e:
            logger.error(f"意图解析失败: {str(e)}")
            # 返回未知意图
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                raw_text=user_input,
                session_id=session_id
            )
    
    async def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的地理信息助手，请严格按照JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析OpenAI响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning(f"无法从响应中提取JSON: {response}")
                return {"intent": "unknown", "confidence": 0.0, "parameters": {}}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}, 响应内容: {response}")
            return {"intent": "unknown", "confidence": 0.0, "parameters": {}} 