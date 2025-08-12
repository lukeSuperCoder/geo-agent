"""
POI搜索插件
"""
from typing import Dict, Any
from loguru import logger

from app.core.plugin_manager import BasePlugin
from app.models.message import PluginType


class POIPlugin(BasePlugin):
    """POI搜索插件"""
    
    def __init__(self):
        super().__init__(
            name="POI搜索",
            description="搜索兴趣点信息"
        )
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        required_params = ["location", "keyword"]
        return all(param in parameters for param in required_params)
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行POI搜索"""
        try:
            location = parameters["location"]
            keyword = parameters["keyword"]
            
            # 模拟POI搜索结果
            poi_data = {
                "location": location,
                "keyword": keyword,
                "results": [
                    {
                        "name": f"{keyword}1",
                        "address": f"{location}某街道1号",
                        "latitude": 39.9042,
                        "longitude": 116.4074,
                        "distance": "500米",
                        "rating": 4.5
                    },
                    {
                        "name": f"{keyword}2", 
                        "address": f"{location}某街道2号",
                        "latitude": 39.9142,
                        "longitude": 116.4174,
                        "distance": "1.2公里",
                        "rating": 4.2
                    }
                ],
                "total_count": 2
            }
            
            logger.info(f"POI搜索成功: {location} - {keyword}")
            return poi_data
            
        except Exception as e:
            logger.error(f"POI搜索失败: {str(e)}")
            raise


# 注册插件
def register_poi_plugin():
    """注册POI插件"""
    from app.core.plugin_manager import plugin_manager
    plugin_manager.register_plugin(PluginType.BAIDU_MAP, POIPlugin()) 