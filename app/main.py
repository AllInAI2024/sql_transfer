import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.config import get_settings, templates, TEMPLATES_DIR, STATIC_DIR
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
    print(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"模板目录: {TEMPLATES_DIR}")
    print(f"静态文件目录: {STATIC_DIR}")
    
    init_db()
    
    yield
    
    print(f"关闭 {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SQL脚本转换工具",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


app.include_router(router_visualization, prefix="/visualization", tags=["可视化脚本"])
app.include_router(router_anonymization, prefix="/anonymization", tags=["匿名化"])
app.include_router(router_conversion, prefix="/conversion", tags=["脚本转换"])
app.include_router(router_validation, prefix="/validation", tags=["验证"])
app.include_router(router_configuration, prefix="/configuration", tags=["配置"])


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "首页",
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION
        }
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "templates_dir": TEMPLATES_DIR,
        "static_dir": STATIC_DIR
    }
