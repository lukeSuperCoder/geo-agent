"""
聊天服务 - 负责处理用户消息和协调各个组件
"""
import json
from typing import Dict, Any, List
from loguru import logger

from app.core.ai_engine import AIEngine
from app.core.plugin_manager import plugin_manager
from app.models.message import (
    UserMessage, IntentResult, PluginRequest, 
    PluginResult, MapAction, ErrorMessage, SystemMessage,
    IntentType, PluginType, MessageType
)


class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self.ai_engine = AIEngine()
        self._register_plugins()
    
    def _register_plugins(self):
        """注册所有插件"""
        from app.plugins.weather_plugin import register_weather_plugin
        from app.plugins.poi_plugin import register_poi_plugin
        
        register_weather_plugin()
        register_poi_plugin()
        logger.info("所有插件注册完成")
    
    async def process_message(self, user_message: UserMessage) -> List[Dict[str, Any]]:
        """处理用户消息，返回响应列表"""
        responses = []
        
        try:
            # 1. 解析用户意图
            intent_result = await self.ai_engine.parse_intent(
                user_message.message, 
                user_message.session_id
            )
            responses.append(intent_result.model_dump())
            
            # 2. 根据意图执行相应操作
            if intent_result.confidence > 0.5:  # 置信度阈值
                plugin_result = await self._handle_intent(intent_result)
                if plugin_result:
                    responses.append(plugin_result.model_dump())
                    
                    # 3. 生成地图操作指令
                    map_action = self._generate_map_action(intent_result, plugin_result)
                    if map_action:
                        responses.append(map_action.model_dump())
            else:
                # 置信度太低，返回错误消息
                error_msg = ErrorMessage(
                    error="抱歉，我没有理解您的意思，请重新描述",
                    session_id=user_message.session_id
                )
                responses.append(error_msg.model_dump())
                
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")
            error_msg = ErrorMessage(
                error="系统处理出错，请稍后重试",
                details=str(e),
                session_id=user_message.session_id
            )
            responses.append(error_msg.model_dump())
        
        return responses
    
    async def _handle_intent(self, intent_result: IntentResult) -> PluginResult:
        """根据意图处理相应的插件调用"""
        try:
            if intent_result.intent == IntentType.WEATHER_QUERY:
                # 天气查询
                location = intent_result.parameters.get("location", "北京")
                plugin_request = PluginRequest(
                    plugin=PluginType.QWEATHER,
                    parameters={"location": location},
                    session_id=intent_result.session_id
                )
                return await plugin_manager.execute_plugin(plugin_request)
                
            elif intent_result.intent == IntentType.POI_SEARCH:
                # POI搜索
                location = intent_result.parameters.get("location", "北京")
                keyword = intent_result.parameters.get("keyword", "餐厅")
                plugin_request = PluginRequest(
                    plugin=PluginType.BAIDU_MAP,
                    parameters={"location": location, "keyword": keyword},
                    session_id=intent_result.session_id
                )
                return await plugin_manager.execute_plugin(plugin_request)
                
            elif intent_result.intent == IntentType.MAP_FLY_TO:
                # 地图飞行
                location = intent_result.parameters.get("location", "北京")
                # 这里可以调用地理编码插件获取坐标
                return None
                
            else:
                logger.warning(f"未处理的意图类型: {intent_result.intent}")
                return None
                
        except Exception as e:
            logger.error(f"处理意图失败: {str(e)}")
            return PluginResult(
                plugin=PluginType.BAIDU_MAP,  # 默认插件类型
                success=False,
                error=str(e),
                session_id=intent_result.session_id
            )
    
    def _generate_map_action(self, intent_result: IntentResult, plugin_result: PluginResult) -> MapAction:
        """根据意图和插件结果生成地图操作指令"""
        try:
            if intent_result.intent == IntentType.WEATHER_QUERY and plugin_result.success:
                # 天气查询成功，飞行到指定位置
                location = intent_result.parameters.get("location", "北京")
                return MapAction(
                    action="fly_to_location",
                    parameters={
                        "location": location,
                        "duration": 3.0,
                        "height": 10000
                    },
                    session_id=intent_result.session_id
                )
                
            elif intent_result.intent == IntentType.POI_SEARCH and plugin_result.success:
                # POI搜索成功，显示标记点
                data = plugin_result.data
                if data and "results" in data:
                    return MapAction(
                        action="add_poi_markers",
                        parameters={
                            "pois": data["results"],
                            "center_location": data.get("location", "北京")
                        },
                        session_id=intent_result.session_id
                    )
                    
            return None
            
        except Exception as e:
            logger.error(f"生成地图操作失败: {str(e)}")
            return None


# 全局聊天服务实例
chat_service = ChatService() 