from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

settings = get_settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

router_anonymization = APIRouter()


@router_anonymization.get("/", response_class=HTMLResponse)
async def anonymization_page(request: Request):
    """
    匿名化处理页面
    """
    return templates.TemplateResponse(
        "anonymization.html",
        {
            "request": request,
            "title": "匿名化",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization"
        }
    )


@router_anonymization.post("/process")
async def process_anonymization():
    """
    执行匿名化处理 API
    """
    # TODO: 实现具体功能
    return {"message": "执行匿名化处理", "data": {}}


@router_anonymization.get("/history")
async def get_anonymization_history():
    """
    获取匿名化历史记录 API
    """
    # TODO: 实现具体功能
    return {"message": "获取匿名化历史记录", "data": []}
