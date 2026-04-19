import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import (
    router_visualization,
    router_anonymization,
    router_conversion,
    router_validation,
    router_configuration
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    print(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库
    init_db()
    
    yield
    
    print(f"关闭 {settings.APP_NAME}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SQL脚本转换工具 - 将基于达梦数据库中间表的可视化脚本转换为直接查询ODPS原始表的新指标脚本",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = settings.STATIC_DIR
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置 Jinja2 模板
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


# 注册路由
app.include_router(router_visualization, prefix="/visualization", tags=["可视化脚本"])
app.include_router(router_anonymization, prefix="/anonymization", tags=["匿名化"])
app.include_router(router_conversion, prefix="/conversion", tags=["脚本转换"])
app.include_router(router_validation, prefix="/validation", tags=["验证"])
app.include_router(router_configuration, prefix="/configuration", tags=["配置"])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    首页
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "首页",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION
        }
    )


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 为模板添加全局上下文
@app.middleware("http")
async def add_template_context(request: Request, call_next):
    """
    为所有请求添加模板上下文
    """
    response = await call_next(request)
    return response
