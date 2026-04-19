from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

settings = get_settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

router_validation = APIRouter()


@router_validation.get("/", response_class=HTMLResponse)
async def validation_page(request: Request):
    """
    验证页面
    """
    return templates.TemplateResponse(
        "validation.html",
        {
            "request": request,
            "title": "验证",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "validation"
        }
    )


@router_validation.post("/execute")
async def execute_validation():
    """
    执行验证 API
    """
    # TODO: 实现具体功能
    return {"message": "执行验证", "data": {}}


@router_validation.get("/history")
async def get_validation_history():
    """
    获取验证历史记录 API
    """
    # TODO: 实现具体功能
    return {"message": "获取验证历史记录", "data": []}


@router_validation.get("/result/{validation_id}")
async def get_validation_result(validation_id: str):
    """
    获取验证结果 API
    """
    # TODO: 实现具体功能
    return {"message": f"获取验证 {validation_id} 结果", "data": {}}
