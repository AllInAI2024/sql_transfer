from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_default_dialects():
    """
    获取默认方言列表
    支持的方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS
    """
    from app.models import Dialect
    return [
        Dialect(
            name='mysql',
            display_name='MySQL',
            description='MySQL 数据库方言',
            is_enabled=True,
            sort_order=1
        ),
        Dialect(
            name='dameng',
            display_name='达梦',
            description='达梦数据库方言',
            is_enabled=True,
            sort_order=2
        ),
        Dialect(
            name='postgresql',
            display_name='PostgreSQL',
            description='PostgreSQL 数据库方言',
            is_enabled=True,
            sort_order=3
        ),
        Dialect(
            name='oracle',
            display_name='ORACLE',
            description='Oracle 数据库方言',
            is_enabled=True,
            sort_order=4
        ),
        Dialect(
            name='odps',
            display_name='ODPS',
            description='阿里云 ODPS (MaxCompute) 数据库方言',
            is_enabled=True,
            sort_order=5
        ),
    ]


def get_default_configs():
    """
    获取默认配置列表
    """
    from app.models import Config
    return [
        Config(
            config_key='llm.api_key',
            config_value='',
            description='OpenAI 兼容 API 的访问密钥',
            category='llm',
            is_sensitive=True
        ),
        Config(
            config_key='llm.api_base',
            config_value='',
            description='API 基础地址（可选，用于兼容其他 API 服务）',
            category='llm',
            is_sensitive=False
        ),
        Config(
            config_key='llm.model_name',
            config_value='gpt-3.5-turbo',
            description='使用的模型名称',
            category='llm',
            is_sensitive=False
        ),
        Config(
            config_key='llm.temperature',
            config_value='0.7',
            description='采样温度（0.0-2.0，越低越确定，越高越随机）',
            category='llm',
            is_sensitive=False
        ),
        Config(
            config_key='llm.max_tokens',
            config_value='4096',
            description='最大生成 token 数',
            category='llm',
            is_sensitive=False
        ),
    ]


def init_db():
    from app.models import Dialect, Task, IntermediateScript, VisualizationScript, Config
    
    Base.metadata.create_all(bind=engine)
    print("数据库表结构创建完成。")
    
    # 插入默认方言数据
    db = SessionLocal()
    try:
        # 检查是否已有方言数据
        from app.models import Dialect
        existing_dialect = db.query(Dialect).filter(Dialect.name == 'mysql').first()
        if existing_dialect:
            print("方言数据已存在，跳过插入。")
        else:
            default_dialects = get_default_dialects()
            for dialect in default_dialects:
                db.add(dialect)
            db.commit()
            print("默认方言数据插入完成（MySQL、达梦、PostgreSQL、ORACLE、ODPS）。")
        
        # 检查是否已有配置数据
        existing_config = db.query(Config).filter(Config.config_key == 'llm.model_name').first()
        if existing_config:
            print("配置数据已存在，跳过插入。")
        else:
            default_configs = get_default_configs()
            for config in default_configs:
                db.add(config)
            db.commit()
            print("默认配置数据插入完成。")
        
        print("数据库初始化完成！")
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        db.close()
