"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # OpenAI配置
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # 第三方API配置
    baidu_map_api_key: Optional[str] = None
    baidu_map_secret_key: Optional[str] = None
    amap_api_key: Optional[str] = None
    qweather_api_key: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/geo_agent.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings() 