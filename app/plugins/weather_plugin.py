"""
天气查询插件
"""
import httpx
from typing import Dict, Any
from loguru import logger

from app.core.plugin_manager import BasePlugin
from app.models.message import PluginType
from app.config import settings


class WeatherPlugin(BasePlugin):
    """天气查询插件"""
    
    def __init__(self):
        super().__init__(
            name="天气查询",
            description="查询指定地区的天气信息"
        )
        self.api_key = settings.qweather_api_key
        self.base_url = "https://devapi.qweather.com/v7"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        required_params = ["location"]
        return all(param in parameters for param in required_params)
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行天气查询"""
        try:
            location = parameters["location"]
            
            # 这里使用模拟数据，实际应该调用和风天气API
            # 由于没有真实的API key，我们返回模拟数据
            weather_data = {
                "location": location,
                "temperature": "25°C",
                "weather": "晴",
                "humidity": "65%",
                "wind": "东南风 3级",
                "air_quality": "优",
                "update_time": "2024-01-01 12:00:00"
            }
            
            logger.info(f"天气查询成功: {location}")
            return weather_data
            
        except Exception as e:
            logger.error(f"天气查询失败: {str(e)}")
            raise


# 注册插件
def register_weather_plugin():
    """注册天气插件"""
    from app.core.plugin_manager import plugin_manager
    plugin_manager.register_plugin(PluginType.QWEATHER, WeatherPlugin()) 