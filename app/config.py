import os
from pathlib import Path

from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

TEMPLATES_DIR = str(APP_DIR / "templates")
STATIC_DIR = str(APP_DIR / "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


class Settings:
    APP_NAME = "SQL脚本转换工具"
    APP_VERSION = "0.1.0"
    DEBUG = True
    
    HOST = "0.0.0.0"
    PORT = 6088
    
    DATABASE_URL = "sqlite:///./sql_transfer.db"
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    
    SECRET_KEY = "your-secret-key-change-in-production"


_settings = Settings()


def get_settings() -> Settings:
    return _settings
