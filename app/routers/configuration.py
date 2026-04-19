from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

settings = get_settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

router_configuration = APIRouter()


@router_configuration.get("/", response_class=HTMLResponse)
async def configuration_page(request: Request):
    """
    配置页面
    """
    return templates.TemplateResponse(
        "configuration.html",
        {
            "request": request,
            "title": "配置",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "configuration"
        }
    )


@router_configuration.get("/settings")
async def get_settings():
    """
    获取当前配置 API
    """
    # TODO: 实现具体功能，注意不要返回敏感信息
    return {
        "message": "获取当前配置",
        "data": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG
        }
    }


@router_configuration.post("/settings")
async def update_settings():
    """
    更新配置 API
    """
    # TODO: 实现具体功能
    return {"message": "更新配置", "data": {}}


@router_configuration.get("/database")
async def get_database_config():
    """
    获取数据库配置 API
    """
    # TODO: 实现具体功能
    return {"message": "获取数据库配置", "data": {}}


@router_configuration.post("/database")
async def update_database_config():
    """
    更新数据库配置 API
    """
    # TODO: 实现具体功能
    return {"message": "更新数据库配置", "data": {}}


@router_configuration.get("/openai")
async def get_openai_config():
    """
    获取 OpenAI 配置 API
    """
    # TODO: 实现具体功能，注意不要返回 API 密钥
    return {
        "message": "获取 OpenAI 配置",
        "data": {
            "model_name": settings.OPENAI_MODEL_NAME,
            "api_base_configured": settings.OPENAI_API_BASE is not None,
            "api_key_configured": settings.OPENAI_API_KEY is not None
        }
    }


@router_configuration.post("/openai")
async def update_openai_config():
    """
    更新 OpenAI 配置 API
    """
    # TODO: 实现具体功能
    return {"message": "更新 OpenAI 配置", "data": {}}
