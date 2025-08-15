"""
Geo-Agent 主应用入口
"""
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import settings
from app.utils.logger import setup_logger
from app.api.websocket import websocket_endpoint
from app.api.chat import router as chat_router
from app.api.pages import router as pages_router


# 创建FastAPI应用
app = FastAPI(
    title="Geo-Agent",
    description="AI驱动的对话式地图可视化平台",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("静态文件服务已启用")
except Exception as e:
    logger.warning(f"静态文件服务启动失败: {str(e)}")

# 注册API路由
app.include_router(chat_router)
app.include_router(pages_router)

# WebSocket路由
@app.websocket("/ws/{session_id}")
async def websocket_route(websocket: WebSocket, session_id: str):
    await websocket_endpoint(websocket, session_id)

@app.websocket("/ws")
async def websocket_route_no_session(websocket: WebSocket):
    await websocket_endpoint(websocket)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "geo-agent"}

# 插件状态
@app.get("/plugins")
async def get_plugins():
    from app.core.plugin_manager import plugin_manager
    return {
        "plugins": plugin_manager.list_plugins(),
        "total": len(plugin_manager.plugins)
    }

# 根路径重定向到聊天页面
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/chat")

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("Geo-Agent 服务启动中...")
    logger.info(f"服务地址: http://{settings.host}:{settings.port}")
    logger.info(f"聊天页面: http://{settings.host}:{settings.port}/chat")
    logger.info(f"WebSocket地址: ws://{settings.host}:{settings.port}/ws")
    logger.info(f"聊天API地址: http://{settings.host}:{settings.port}/api/chat/stream")
    logger.info(f"测试页面: http://{settings.host}:{settings.port}/test")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Geo-Agent 服务关闭中...")


if __name__ == "__main__":
    # 设置日志
    setup_logger()
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 