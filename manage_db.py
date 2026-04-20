#!/usr/bin/env python3
"""
数据库管理脚本
用于初始化 SQLite 数据库、清除数据和重置数据库

使用方法：
    python manage_db.py init      # 初始化数据库（创建表结构，插入默认配置和方言）
    python manage_db.py clear     # 清除所有数据（保留表结构）
    python manage_db.py reset     # 重置数据库（删除所有表并重新创建）
    python manage_db.py status    # 查看数据库状态

表关系说明：
    - dialects（方言表）存储支持的数据库方言
    - tasks（任务表）通过三个方言字段关联 dialects
    - visualization_scripts（可视化脚本表）依赖于 tasks（外键）
    - intermediate_scripts（中间脚本表）独立存在，与任务无关
    - configs（配置表）独立存在
"""

import argparse
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models import Dialect, Task, IntermediateScript, VisualizationScript, Config


def get_default_dialects():
    """
    获取默认方言列表
    支持的方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS
    """
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
    """
    初始化数据库
    - 创建所有表结构
    - 插入默认方言数据
    - 插入默认配置数据
    """
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)
    
    settings = get_settings()
    print(f"数据库地址: {settings.DATABASE_URL}")
    
    # 创建所有表
    print("\n创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("✓ 表结构创建完成")
    
    db = SessionLocal()
    try:
        # 插入默认方言
        print("\n插入默认方言数据...")
        existing_dialect = db.query(Dialect).filter(Dialect.name == 'mysql').first()
        if existing_dialect:
            print("  方言数据已存在，跳过插入")
        else:
            default_dialects = get_default_dialects()
            for dialect in default_dialects:
                db.add(dialect)
            db.commit()
            print("✓ 默认方言数据插入完成")
        
        # 插入默认配置
        print("\n插入默认配置数据...")
        existing_config = db.query(Config).filter(Config.config_key == 'llm.model_name').first()
        if existing_config:
            print("  配置数据已存在，跳过插入")
        else:
            default_configs = get_default_configs()
            for config in default_configs:
                db.add(config)
            db.commit()
            print("✓ 默认配置数据插入完成")
        
        print("\n" + "=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        
        # 显示表列表
        show_tables(db)
        
        # 显示重要说明
        print("\n📌 重要说明：")
        print("   - dialects（方言表）存储支持的数据库方言")
        print("   - tasks（任务表）通过三个方言字段关联方言表")
        print("   - 支持的方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS")
        print("   - intermediate_scripts（中间脚本表）是独立存在的，与任务无关")
        print("   - 删除任务时不会影响中间表")
        print("   - 中间表名全局唯一")
        
    except Exception as e:
        db.rollback()
        print(f"✗ 初始化失败: {e}")
        raise
    finally:
        db.close()


def clear_data():
    """
    清除所有数据
    - 清空所有表的数据
    - 保留表结构
    - 重置自增 ID
    
    注意：
    - 清除顺序需要考虑外键约束
    - visualization_scripts 依赖 tasks
    - tasks 依赖 dialects（三个外键字段）
    - intermediate_scripts 和 configs 独立存在
    """
    print("=" * 50)
    print("开始清除数据库数据...")
    print("=" * 50)
    
    confirm = input("\n警告：此操作将删除所有数据，是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    db = SessionLocal()
    try:
        # 清除数据的顺序（考虑外键约束）
        # 1. visualization_scripts 依赖 tasks，先清除
        # 2. tasks 依赖 dialects（三个外键），先清除
        # 3. dialects、intermediate_scripts、configs 独立存在
        tables_order = [
            'visualization_scripts',  # 依赖 tasks，先清除
            'tasks',                    # 被 visualization_scripts 依赖，依赖 dialects
            'intermediate_scripts',     # 独立存在
            'configs',                  # 独立存在
            'dialects'                  # 被 tasks 依赖
        ]
        
        print("\n清除表数据...")
        for table_name in tables_order:
            # 使用 SQL 直接删除
            db.execute(text(f"DELETE FROM {table_name}"))
            print(f"  ✓ 已清除: {table_name}")
        
        # 重置 SQLite 的自增计数器
        print("\n重置自增计数器...")
        db.execute(text("DELETE FROM sqlite_sequence"))
        print("  ✓ 自增计数器已重置")
        
        db.commit()
        
        print("\n" + "=" * 50)
        print("数据清除完成！")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"✗ 清除数据失败: {e}")
        raise
    finally:
        db.close()


def reset_db():
    """
    重置数据库
    - 删除所有表
    - 重新创建表结构
    - 插入默认方言和配置
    """
    print("=" * 50)
    print("开始重置数据库...")
    print("=" * 50)
    
    confirm = input("\n警告：此操作将删除所有表和数据，是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    # 先删除所有表
    print("\n删除所有表...")
    Base.metadata.drop_all(bind=engine)
    print("  ✓ 所有表已删除")
    
    # 重新初始化
    init_db()


def show_status():
    """
    查看数据库状态
    """
    print("=" * 50)
    print("数据库状态")
    print("=" * 50)
    
    settings = get_settings()
    print(f"\n数据库地址: {settings.DATABASE_URL}")
    
    # 检查数据库文件是否存在
    if settings.DATABASE_URL.startswith('sqlite:///'):
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"数据库文件大小: {file_size / 1024:.2f} KB")
        else:
            print("数据库文件不存在")
    
    db = SessionLocal()
    try:
        show_tables(db)
        
        # 显示表关系说明
        print("\n📋 表关系说明：")
        print("   ┌─────────────────────────────────────────────────────────────┐")
        print("   │  dialects (方言表)                                          │")
        print("   │       ▲        ▲               ▲                            │")
        print("   │       │        │               │                            │")
        print("   │       └────────┼───────────────┘                            │")
        print("   │                │                                            │")
        print("   │  tasks (任务表) ◄──────────────────────────────────────────│")
        print("   │  (intermediate_dialect_id, visualization_dialect_id,     │")
        print("   │   converted_dialect_id 三个外键关联 dialects)             │")
        print("   │       │                                                     │")
        print("   │       └──►  visualization_scripts (可视化脚本表)           │")
        print("   │                     │                                      │")
        print("   │                     └──►  (通过 intermediate_table_names) │")
        print("   │                                   │                         │")
        print("   │                                   ▼                         │")
        print("   │  intermediate_scripts (中间脚本表) ◄──────────────────────│")
        print("   │  (独立存在，与任务无关)                                    │")
        print("   │                                                            │")
        print("   │  configs (配置表)                                          │")
        print("   │  (独立存在)                                                │")
        print("   └─────────────────────────────────────────────────────────────┘")
        
    except Exception as e:
        print(f"无法获取表信息: {e}")
    finally:
        db.close()


def show_tables(db):
    """
    显示表信息
    """
    print("\n" + "-" * 50)
    print("表信息")
    print("-" * 50)
    
    # 获取所有表名
    result = db.execute(text("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """))
    tables = [row[0] for row in result]
    
    if not tables:
        print("  没有找到表")
        return
    
    for table_name in tables:
        # 获取表的记录数
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = count_result.fetchone()[0]
        
        # 获取表结构
        columns_result = db.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in columns_result]
        
        print(f"\n📋 {table_name}")
        print(f"   记录数: {count}")
        print(f"   字段: {', '.join(columns)}")


def main():
    parser = argparse.ArgumentParser(
        description='数据库管理脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python manage_db.py init      初始化数据库
  python manage_db.py clear     清除所有数据
  python manage_db.py reset     重置数据库
  python manage_db.py status    查看数据库状态

表关系：
  - dialects 存储支持的数据库方言
  - tasks 通过三个外键关联 dialects
  - visualization_scripts 依赖 tasks
  - intermediate_scripts 独立存在，与任务无关
  - configs 独立存在

支持的方言：
  - MySQL
  - 达梦
  - PostgreSQL
  - ORACLE
  - ODPS (MaxCompute)
        """
    )
    
    parser.add_argument(
        'action',
        choices=['init', 'clear', 'reset', 'status'],
        help='操作类型: init(初始化), clear(清除数据), reset(重置), status(状态)'
    )
    
    args = parser.parse_args()
    
    actions = {
        'init': init_db,
        'clear': clear_data,
        'reset': reset_db,
        'status': show_status,
    }
    
    actions[args.action]()


if __name__ == '__main__':
    main()
