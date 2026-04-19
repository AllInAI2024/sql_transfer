from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings

settings = get_settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

router_conversion = APIRouter()


@router_conversion.get("/", response_class=HTMLResponse)
async def conversion_page(request: Request):
    """
    脚本转换页面
    """
    return templates.TemplateResponse(
        "conversion.html",
        {
            "request": request,
            "title": "脚本转换",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "conversion"
        }
    )


@router_conversion.post("/start")
async def start_conversion():
    """
    开始脚本转换 API
    """
    # TODO: 实现具体功能
    return {"message": "开始脚本转换", "task_id": None}


@router_conversion.get("/status/{task_id}")
async def get_conversion_status(task_id: str):
    """
    获取转换任务状态 API
    """
    # TODO: 实现具体功能
    return {"message": f"获取转换任务 {task_id} 状态", "status": "pending"}


@router_conversion.get("/stream/{task_id}")
async def stream_conversion_progress(task_id: str):
    """
    流式获取转换进度 (SSE)
    """
    # TODO: 实现具体功能
    # 这里应该返回 EventSourceResponse
    return {"message": f"流式获取转换任务 {task_id} 进度"}


@router_conversion.get("/history")
async def get_conversion_history():
    """
    获取转换历史记录 API
    """
    # TODO: 实现具体功能
    return {"message": "获取转换历史记录", "data": []}


@router_conversion.get("/result/{task_id}")
async def get_conversion_result(task_id: str):
    """
    获取转换结果 API
    """
    # TODO: 实现具体功能
    return {"message": f"获取转换任务 {task_id} 结果", "data": {}}
