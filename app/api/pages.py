"""
页面路由模块 - 提供前端页面访问
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["pages"])

# 获取静态文件目录
static_dir = Path(__file__).parent.parent.parent / "static"
templates = Jinja2Templates(directory=str(static_dir))


@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """聊天页面"""
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page_alt(request: Request):
    """聊天页面（备用路径）"""
    return templates.TemplateResponse("chat.html", {"request": request})
