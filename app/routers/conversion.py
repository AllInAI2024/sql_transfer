from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings, templates

settings = get_settings()

router_conversion = APIRouter()


@router_conversion.get("/", response_class=HTMLResponse)
async def conversion_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="conversion.html",
        context={
            "title": "脚本转换",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "conversion"
        }
    )


@router_conversion.post("/start")
async def start_conversion():
    return {"message": "开始脚本转换", "task_id": None}


@router_conversion.get("/status/{task_id}")
async def get_conversion_status(task_id: str):
    return {"message": f"获取转换任务 {task_id} 状态", "status": "pending"}


@router_conversion.get("/stream/{task_id}")
async def stream_conversion_progress(task_id: str):
    return {"message": f"流式获取转换任务 {task_id} 进度"}


@router_conversion.get("/history")
async def get_conversion_history():
    return {"message": "获取转换历史记录", "data": []}


@router_conversion.get("/result/{task_id}")
async def get_conversion_result(task_id: str):
    return {"message": f"获取转换任务 {task_id} 结果", "data": {}}
