from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings, templates

settings = get_settings()

router_validation = APIRouter()


@router_validation.get("/", response_class=HTMLResponse)
async def validation_page(request: Request):
    return templates.TemplateResponse(
        name="validation.html",
        context={
            "request": request,
            "title": "验证",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "validation"
        }
    )


@router_validation.post("/execute")
async def execute_validation():
    return {"message": "执行验证", "data": {}}


@router_validation.get("/history")
async def get_validation_history():
    return {"message": "获取验证历史记录", "data": []}


@router_validation.get("/result/{validation_id}")
async def get_validation_result(validation_id: str):
    return {"message": f"获取验证 {validation_id} 结果", "data": {}}
