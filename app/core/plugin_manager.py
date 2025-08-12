"""
插件管理器 - 负责插件的注册、管理和调用
"""
from typing import Dict, Any, Optional, Type
from abc import ABC, abstractmethod
from loguru import logger

from app.models.message import PluginType, PluginResult, PluginRequest


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件功能"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数"""
        pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[PluginType, BasePlugin] = {}
    
    def register_plugin(self, plugin_type: PluginType, plugin: BasePlugin):
        """注册插件"""
        self.plugins[plugin_type] = plugin
        logger.info(f"插件注册成功: {plugin_type} - {plugin.name}")
    
    def get_plugin(self, plugin_type: PluginType) -> Optional[BasePlugin]:
        """获取插件"""
        return self.plugins.get(plugin_type)
    
    def list_plugins(self) -> Dict[PluginType, str]:
        """列出所有插件"""
        return {plugin_type: plugin.name for plugin_type, plugin in self.plugins.items()}
    
    async def execute_plugin(self, request: PluginRequest) -> PluginResult:
        """执行插件"""
        try:
            plugin = self.get_plugin(request.plugin)
            if not plugin:
                return PluginResult(
                    plugin=request.plugin,
                    success=False,
                    error=f"插件未找到: {request.plugin}",
                    session_id=request.session_id
                )
            
            # 验证参数
            if not plugin.validate_parameters(request.parameters):
                return PluginResult(
                    plugin=request.plugin,
                    success=False,
                    error="参数验证失败",
                    session_id=request.session_id
                )
            
            # 执行插件
            logger.info(f"执行插件: {request.plugin}")
            result_data = await plugin.execute(request.parameters)
            
            return PluginResult(
                plugin=request.plugin,
                success=True,
                data=result_data,
                session_id=request.session_id
            )
            
        except Exception as e:
            logger.error(f"插件执行失败: {str(e)}")
            return PluginResult(
                plugin=request.plugin,
                success=False,
                error=str(e),
                session_id=request.session_id
            )


# 全局插件管理器实例
plugin_manager = PluginManager() 