from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.config import get_settings, templates

settings = get_settings()

router_configuration = APIRouter()


class AnonymizationConfigUpdate(BaseModel):
    exclude_list: Optional[str] = None


@router_configuration.get("/", response_class=HTMLResponse)
async def configuration_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="configuration.html",
        context={
            "title": "配置",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "configuration",
            "anonymization_exclude_list": settings.ANONYMIZATION_EXCLUDE_LIST
        }
    )


@router_configuration.get("/settings")
async def get_config_settings():
    return {
        "message": "获取当前配置",
        "data": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "debug": settings.DEBUG
        }
    }


@router_configuration.post("/settings")
async def update_config_settings():
    return {"message": "更新配置", "data": {}}


@router_configuration.get("/database")
async def get_database_config():
    return {"message": "获取数据库配置", "data": {}}


@router_configuration.post("/database")
async def update_database_config():
    return {"message": "更新数据库配置", "data": {}}


@router_configuration.get("/openai")
async def get_openai_config():
    return {
        "message": "获取 OpenAI 配置",
        "data": {
            "model_name": settings.OPENAI_MODEL_NAME,
            "api_base_configured": bool(settings.OPENAI_API_BASE),
            "api_key_configured": bool(settings.OPENAI_API_KEY)
        }
    }


@router_configuration.post("/openai")
async def update_openai_config():
    return {"message": "更新 OpenAI 配置", "data": {}}


@router_configuration.get("/anonymization")
async def get_anonymization_config():
    return {
        "success": True,
        "exclude_list": settings.ANONYMIZATION_EXCLUDE_LIST
    }


@router_configuration.post("/anonymization")
async def update_anonymization_config(config: AnonymizationConfigUpdate):
    if config.exclude_list is not None:
        settings.ANONYMIZATION_EXCLUDE_LIST = config.exclude_list
    return {
        "success": True,
        "message": "匿名化配置已保存"
    }
