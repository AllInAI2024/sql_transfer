# SQL 脚本转换工具

## 项目目标

开发一个 SQL 脚本转换的 Web 项目，将基于达梦数据库中间表的可视化脚本，转换为直接查询 ODPS (MaxCompute) 原始表的新指标脚本。

## 转换本质

- 可视化脚本查询达梦数据库的中间表（通过中间表脚本从 ODPS 原始表构建）
- 中间表脚本定义了中间表如何从 ODPS 原始表获取数据
- 转换时需要分析中间表脚本，理解 ODPS 原始表的结构和查询逻辑
- 结合两者生成直接查询 ODPS 原始表的新脚本，跳过中间表

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 前端渲染 | Jinja2 (服务端渲染) |
| Python版本 | 3.11+ |
| 依赖管理 | uv |
| 数据库 | SQLite |
| ORM | SQLAlchemy |
| SQL解析 | sqlparse |
| 智能体框架 | LangChain |
| 大模型API | OpenAI兼容API |
| 流式输出 | SSE (Server-Sent Events) |
| 服务端口 | 6088 |

## 项目结构

```
sql_transfer/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库连接和初始化
│   ├── models/              # 数据模型
│   │   └── __init__.py
│   ├── routers/             # 路由
│   │   └── __init__.py
│   ├── templates/           # Jinja2 模板
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── visualization_scripts.html
│   │   ├── anonymization.html
│   │   ├── conversion.html
│   │   ├── validation.html
│   │   └── configuration.html
│   └── static/              # 静态文件
│       └── style.css
├── database.sql             # 数据库初始化脚本
├── pyproject.toml           # 项目配置和依赖
├── README.md
└── .gitignore
```

## 功能模块

1. **可视化脚本** - 管理和查看可视化脚本
2. **匿名化** - 对脚本进行匿名化处理
3. **脚本转换** - 核心转换功能，将中间表脚本转换为直接查询 ODPS 的脚本
4. **验证** - 验证转换后的脚本正确性
5. **配置** - 系统配置管理

## 数据库设计

### 任务表 (tasks)
- 任务名
- 每个任务包括多个 SQL 脚本

### 中间脚本表 (intermediate_scripts)
- 中间表名
- 脚本

### 可视化脚本表 (visualization_scripts)
- 脚本名
- 对应的中间表名（可能 1 个或多个）
- 可视化脚本
- 整合脚本（把该可视化脚本和对应的中间表脚本整合成一个脚本）
- 匿名化整合脚本
- 转换后新脚本

所有表均包含主键、创建时间、修改时间等非业务字段。

## 快速开始

### 环境要求
- Python 3.11+
- uv (Python 包管理工具)

### 安装依赖

```bash
# 使用 uv 安装依赖
uv sync
```

### 初始化数据库

```bash
# 执行数据库初始化脚本
uv run python -c "from app.database import init_db; init_db()"
```

### 启动服务

```bash
# 启动开发服务器
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 6088
```

服务启动后访问: http://localhost:6088

## 开发说明

- 后端使用 FastAPI 框架
- 前端采用服务端渲染的 Jinja2 模板
- 数据库操作使用 SQLAlchemy ORM
- SQL 解析使用 sqlparse 库
- 大模型集成使用 LangChain 框架

## 许可证

MIT License