from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings, templates
from app.database import get_db
from app.models.models import Dialect, Task, VisualizationScript
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


class TaskCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    intermediate_dialect_id: int
    visualization_dialect_id: int
    converted_dialect_id: int


class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    intermediate_dialect_id: Optional[int] = None
    intermediate_dialect_name: Optional[str] = None
    visualization_dialect_id: Optional[int] = None
    visualization_dialect_name: Optional[str] = None
    converted_dialect_id: Optional[int] = None
    converted_dialect_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    visualization_script_count: int = 0


class TaskListResponse(BaseModel):
    success: bool
    tasks: List[TaskResponse] = []
    error: Optional[str] = None


class TaskDeleteResponse(BaseModel):
    success: bool
    error: Optional[str] = None


class DialectOption(BaseModel):
    id: int
    name: str
    display_name: str


class DialectListResponse(BaseModel):
    success: bool
    dialects: List[DialectOption] = []


@router_anonymization.get("/", response_class=HTMLResponse)
async def anonymization_page(request: Request, db: Session = Depends(get_db)):
    dialects = db.query(Dialect).filter(Dialect.is_enabled == True).order_by(Dialect.sort_order).all()
    
    tasks = db.query(Task).order_by(Task.updated_at.desc()).all()
    
    task_responses = []
    for task in tasks:
        vis_count = len(task.visualization_scripts) if task.visualization_scripts else 0
        task_responses.append(TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            intermediate_dialect_id=task.intermediate_dialect_id,
            intermediate_dialect_name=task.intermediate_dialect.display_name if task.intermediate_dialect else None,
            visualization_dialect_id=task.visualization_dialect_id,
            visualization_dialect_name=task.visualization_dialect.display_name if task.visualization_dialect else None,
            converted_dialect_id=task.converted_dialect_id,
            converted_dialect_name=task.converted_dialect.display_name if task.converted_dialect else None,
            created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
            updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None,
            visualization_script_count=vis_count
        ))
    
    dialect_options = [
        DialectOption(id=d.id, name=d.name, display_name=d.display_name)
        for d in dialects
    ]
    
    return templates.TemplateResponse(
        request=request,
        name="anonymization.html",
        context={
            "title": "匿名化",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization",
            "dialects": dialect_options,
            "tasks": task_responses,
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


@router_anonymization.get("/api/dialects", response_model=DialectListResponse)
async def get_dialects(db: Session = Depends(get_db)):
    try:
        dialects = db.query(Dialect).filter(Dialect.is_enabled == True).order_by(Dialect.sort_order).all()
        return DialectListResponse(
            success=True,
            dialects=[
                DialectOption(id=d.id, name=d.name, display_name=d.display_name)
                for d in dialects
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_anonymization.post("/api/tasks", response_model=TaskResponse)
async def create_task(request: TaskCreateRequest, db: Session = Depends(get_db)):
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="任务名称不能为空")
        
        if request.intermediate_dialect_id != request.converted_dialect_id:
            raise HTTPException(
                status_code=400, 
                detail="中间表方言和转换脚本方言必须相同（因为两者都是基于原始数据的脚本）"
            )
        
        intermediate_dialect = db.query(Dialect).filter(Dialect.id == request.intermediate_dialect_id).first()
        visualization_dialect = db.query(Dialect).filter(Dialect.id == request.visualization_dialect_id).first()
        converted_dialect = db.query(Dialect).filter(Dialect.id == request.converted_dialect_id).first()
        
        if not intermediate_dialect:
            raise HTTPException(status_code=400, detail="中间表方言不存在")
        if not visualization_dialect:
            raise HTTPException(status_code=400, detail="可视化脚本方言不存在")
        if not converted_dialect:
            raise HTTPException(status_code=400, detail="转换脚本方言不存在")
        
        existing_task = db.query(Task).filter(Task.name == request.name.strip()).first()
        if existing_task:
            raise HTTPException(status_code=400, detail=f"任务名称 '{request.name}' 已存在")
        
        task = Task(
            name=request.name.strip(),
            description=request.description,
            intermediate_dialect_id=request.intermediate_dialect_id,
            visualization_dialect_id=request.visualization_dialect_id,
            converted_dialect_id=request.converted_dialect_id
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return TaskResponse(
            id=task.id,
            name=task.name,
            description=task.description,
            intermediate_dialect_id=task.intermediate_dialect_id,
            intermediate_dialect_name=intermediate_dialect.display_name,
            visualization_dialect_id=task.visualization_dialect_id,
            visualization_dialect_name=visualization_dialect.display_name,
            converted_dialect_id=task.converted_dialect_id,
            converted_dialect_name=converted_dialect.display_name,
            created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
            updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None,
            visualization_script_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router_anonymization.get("/api/tasks", response_model=TaskListResponse)
async def list_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).order_by(Task.updated_at.desc()).all()
        
        task_responses = []
        for task in tasks:
            vis_count = len(task.visualization_scripts) if task.visualization_scripts else 0
            task_responses.append(TaskResponse(
                id=task.id,
                name=task.name,
                description=task.description,
                intermediate_dialect_id=task.intermediate_dialect_id,
                intermediate_dialect_name=task.intermediate_dialect.display_name if task.intermediate_dialect else None,
                visualization_dialect_id=task.visualization_dialect_id,
                visualization_dialect_name=task.visualization_dialect.display_name if task.visualization_dialect else None,
                converted_dialect_id=task.converted_dialect_id,
                converted_dialect_name=task.converted_dialect.display_name if task.converted_dialect else None,
                created_at=task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
                updated_at=task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None,
                visualization_script_count=vis_count
            ))
        
        return TaskListResponse(success=True, tasks=task_responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_anonymization.delete("/api/tasks/{task_id}", response_model=TaskDeleteResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail=f"任务 ID {task_id} 不存在")
        
        vis_script_count = db.query(VisualizationScript).filter(
            VisualizationScript.task_id == task_id
        ).count()
        
        db.delete(task)
        db.commit()
        
        return TaskDeleteResponse(
            success=True,
            error=f"任务已删除，同时删除了 {vis_script_count} 个关联的可视化脚本"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router_anonymization.get("/task/{task_id}", response_class=HTMLResponse)
async def task_detail_page(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    visualization_scripts = db.query(VisualizationScript).filter(
        VisualizationScript.task_id == task_id
    ).order_by(VisualizationScript.updated_at.desc()).all()
    
    script_list = []
    for vs in visualization_scripts:
        script_list.append({
            "id": vs.id,
            "name": vs.name,
            "intermediate_table_names": vs.intermediate_table_names,
            "description": vs.description,
            "has_integrated_script": bool(vs.integrated_script),
            "has_anonymized_script": bool(vs.anonymized_integrated_script),
            "has_converted_script": bool(vs.converted_script),
            "created_at": vs.created_at.strftime('%Y-%m-%d %H:%M:%S') if vs.created_at else None,
            "updated_at": vs.updated_at.strftime('%Y-%m-%d %H:%M:%S') if vs.updated_at else None,
        })
    
    return templates.TemplateResponse(
        request=request,
        name="task_detail.html",
        context={
            "title": f"任务详情 - {task.name}",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "anonymization",
            "task": {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "intermediate_dialect_name": task.intermediate_dialect.display_name if task.intermediate_dialect else None,
                "visualization_dialect_name": task.visualization_dialect.display_name if task.visualization_dialect else None,
                "converted_dialect_name": task.converted_dialect.display_name if task.converted_dialect else None,
                "created_at": task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
                "updated_at": task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else None,
            },
            "scripts": script_list,
        }
    )
