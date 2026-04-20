from typing import Dict, List, Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.config import get_settings, templates
from app.services.anonymization_service import anonymize_sql, deanonymize_sql

settings = get_settings()

router_anonymization = APIRouter()


class AnonymizeRequest(BaseModel):
    sql: str
    exclude_list: Optional[str] = None
    dialect: Optional[str] = None
    remove_comments: Optional[bool] = True


class DeanonymizeRequest(BaseModel):
    sql: str
    mapping: Dict[str, Dict[str, str]]
    dialect: Optional[str] = None


class AnonymizeResponse(BaseModel):
    success: bool
    anonymized_sql: Optional[str] = None
    mapping: Optional[Dict[str, Dict[str, str]]] = None
    error: Optional[str] = None


class DeanonymizeResponse(BaseModel):
    success: bool
    deanonymized_sql: Optional[str] = None
    error: Optional[str] = None


class ConfigResponse(BaseModel):
    success: bool
    exclude_list: str
    dialect: str


@router_anonymization.get("/", response_class=HTMLResponse)
async def anonymization_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="anonymization.html",
        context={
            "title": "匿名化",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization",
        }
    )


@router_anonymization.get("/test", response_class=HTMLResponse)
async def anonymization_test_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="anonymization_test.html",
        context={
            "title": "匿名化测试",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization",
            "default_exclude_list": settings.ANONYMIZATION_EXCLUDE_LIST,
        }
    )


@router_anonymization.post("/process", response_model=AnonymizeResponse)
async def process_anonymization(request: AnonymizeRequest):
    try:
        if not request.sql or not request.sql.strip():
            return AnonymizeResponse(
                success=False,
                error="SQL 脚本不能为空"
            )
        
        exclude_list_str = request.exclude_list or settings.ANONYMIZATION_EXCLUDE_LIST
        exclude_list = [item.strip() for item in exclude_list_str.split(",") if item.strip()]
        
        dialect = request.dialect or settings.ANONYMIZATION_DEFAULT_DIALECT
        
        anonymized_sql, mapping = anonymize_sql(
            sql=request.sql,
            exclude_list=exclude_list,
            dialect=dialect,
            remove_comments=request.remove_comments or False
        )
        
        return AnonymizeResponse(
            success=True,
            anonymized_sql=anonymized_sql,
            mapping=mapping
        )
    except Exception as e:
        return AnonymizeResponse(
            success=False,
            error=f"匿名化处理失败: {str(e)}"
        )


@router_anonymization.post("/test/process", response_model=AnonymizeResponse)
async def test_process_anonymization(request: AnonymizeRequest):
    return await process_anonymization(request)


@router_anonymization.post("/test/deanonymize", response_model=DeanonymizeResponse)
async def test_process_deanonymization(request: DeanonymizeRequest):
    try:
        if not request.sql or not request.sql.strip():
            return DeanonymizeResponse(
                success=False,
                error="SQL 脚本不能为空"
            )
        
        if not request.mapping:
            return DeanonymizeResponse(
                success=False,
                error="编码字典不能为空"
            )
        
        dialect = request.dialect or settings.ANONYMIZATION_DEFAULT_DIALECT
        
        deanonymized_sql = deanonymize_sql(
            sql=request.sql,
            mapping=request.mapping,
            dialect=dialect
        )
        
        return DeanonymizeResponse(
            success=True,
            deanonymized_sql=deanonymized_sql
        )
    except Exception as e:
        return DeanonymizeResponse(
            success=False,
            error=f"反向匿名化处理失败: {str(e)}"
        )


@router_anonymization.get("/config", response_model=ConfigResponse)
async def get_anonymization_config():
    return ConfigResponse(
        success=True,
        exclude_list=settings.ANONYMIZATION_EXCLUDE_LIST,
        dialect=settings.ANONYMIZATION_DEFAULT_DIALECT
    )


@router_anonymization.get("/history")
async def get_anonymization_history():
    return {"message": "获取匿名化历史记录", "data": []}
