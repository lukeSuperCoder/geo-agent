"""
消息数据模型
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageType(str, Enum):
    """消息类型枚举"""
    USER_INPUT = "user_input"
    INTENT_PARSED = "intent_parsed"
    PLUGIN_EXECUTING = "plugin_executing"
    PLUGIN_RESULT = "plugin_result"
    MAP_ACTION = "map_action"
    ERROR = "error"
    SYSTEM = "system"


class IntentType(str, Enum):
    """意图类型枚举"""
    WEATHER_QUERY = "weather_query"
    POI_SEARCH = "poi_search"
    ROUTE_PLANNING = "route_planning"
    MAP_FLY_TO = "map_fly_to"
    LOCATION_SEARCH = "location_search"
    UNKNOWN = "unknown"


class PluginType(str, Enum):
    """插件类型枚举"""
    BAIDU_MAP = "baidu_map"
    AMAP = "amap"
    QWEATHER = "qweather"
    GEONAMES = "geonames"


class UserMessage(BaseModel):
    """用户输入消息"""
    type: MessageType = MessageType.USER_INPUT
    message: str
    session_id: str
    timestamp: Optional[float] = None


class IntentResult(BaseModel):
    """意图解析结果"""
    type: MessageType = MessageType.INTENT_PARSED
    intent: IntentType
    confidence: float
    parameters: Dict[str, Any]
    raw_text: str
    session_id: str


class PluginRequest(BaseModel):
    """插件请求"""
    type: MessageType = MessageType.PLUGIN_EXECUTING
    plugin: PluginType
    parameters: Dict[str, Any]
    session_id: str


class PluginResult(BaseModel):
    """插件执行结果"""
    type: MessageType = MessageType.PLUGIN_RESULT
    plugin: PluginType
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    session_id: str


class MapAction(BaseModel):
    """地图操作指令"""
    type: MessageType = MessageType.MAP_ACTION
    action: str  # fly_to, add_marker, add_path, etc.
    parameters: Dict[str, Any]
    session_id: str


class ErrorMessage(BaseModel):
    """错误消息"""
    type: MessageType = MessageType.ERROR
    error: str
    details: Optional[str] = None
    session_id: str


class SystemMessage(BaseModel):
    """系统消息"""
    type: MessageType = MessageType.SYSTEM
    message: str
    session_id: str 