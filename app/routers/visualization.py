from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

settings = get_settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

router_visualization = APIRouter()


@router_visualization.get("/", response_class=HTMLResponse)
async def visualization_scripts(request: Request):
    """
    可视化脚本管理页面
    """
    return templates.TemplateResponse(
        "visualization_scripts.html",
        {
            "request": request,
            "title": "可视化脚本",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "active_menu": "visualization"
        }
    )


@router_visualization.get("/list")
async def list_visualization_scripts():
    """
    获取可视化脚本列表 API
    """
    # TODO: 实现具体功能
    return {"message": "获取可视化脚本列表", "data": []}


@router_visualization.get("/{script_id}")
async def get_visualization_script(script_id: int):
    """
    获取单个可视化脚本详情 API
    """
    # TODO: 实现具体功能
    return {"message": f"获取可视化脚本 {script_id}", "data": {}}


@router_visualization.post("/")
async def create_visualization_script():
    """
    创建可视化脚本 API
    """
    # TODO: 实现具体功能
    return {"message": "创建可视化脚本", "data": {}}


@router_visualization.put("/{script_id}")
async def update_visualization_script(script_id: int):
    """
    更新可视化脚本 API
    """
    # TODO: 实现具体功能
    return {"message": f"更新可视化脚本 {script_id}", "data": {}}


@router_visualization.delete("/{script_id}")
async def delete_visualization_script(script_id: int):
    """
    删除可视化脚本 API
    """
    # TODO: 实现具体功能
    return {"message": f"删除可视化脚本 {script_id}"}
