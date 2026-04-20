from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings, templates

settings = get_settings()

router_anonymization = APIRouter()


@router_anonymization.get("/", response_class=HTMLResponse)
async def anonymization_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="anonymization.html",
        context={
            "title": "匿名化",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization"
        }
    )


@router_anonymization.post("/process")
async def process_anonymization():
    return {"message": "执行匿名化处理", "data": {}}


@router_anonymization.get("/history")
async def get_anonymization_history():
    return {"message": "获取匿名化历史记录", "data": []}
