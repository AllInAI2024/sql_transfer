#!/usr/bin/env python3
"""
数据库管理脚本
用于初始化 SQLite 数据库、清除数据和重置数据库

使用方法：
    python manage_db.py init      # 初始化数据库（创建表结构，插入默认配置）
    python manage_db.py clear     # 清除所有数据（保留表结构）
    python manage_db.py reset     # 重置数据库（删除所有表并重新创建）
    python manage_db.py status    # 查看数据库状态
"""

import argparse
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models import Task, IntermediateScript, VisualizationScript, Config


def init_db():
    """
    初始化数据库
    - 创建所有表结构
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
    
    # 插入默认配置
    print("\n插入默认配置数据...")
    db = SessionLocal()
    try:
        # 检查是否已有配置
        existing_config = db.query(Config).filter(Config.config_key == 'llm.model_name').first()
        if existing_config:
            print("  配置数据已存在，跳过插入")
        else:
            # LLM 默认配置
            default_configs = [
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
            
            for config in default_configs:
                db.add(config)
            
            db.commit()
            print("✓ 默认配置数据插入完成")
        
        print("\n" + "=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        
        # 显示表列表
        show_tables(db)
        
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
        tables_order = [
            'visualization_scripts',
            'intermediate_scripts',
            'tasks',
            'configs'  # 配置表也可以选择清除，或者保留
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
    - 插入默认配置
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
