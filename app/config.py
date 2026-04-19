import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "SQL脚本转换工具"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 6088
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sql_transfer.db"
    
    # OpenAI 兼容 API 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo"
    
    # 其他配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), "templates")
    STATIC_DIR: str = os.path.join(os.path.dirname(__file__), "static")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
