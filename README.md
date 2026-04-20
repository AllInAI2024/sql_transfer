# SQL 脚本转换工具

## 项目目标

开发一个 SQL 脚本转换的 Web 项目，具备高度扩展性和实用性，支持多种数据库方言之间的脚本转换。

**核心特性**：
- 支持多种数据库方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS 等
- 一次任务可灵活指定三个脚本的方言：
  - 中间表脚本方言（源表方言）
  - 可视化脚本方言（查询方言）
  - 转换后脚本方言（目标方言）
- 方言配置存储在数据库中，便于扩展和管理

## 转换本质

- 可视化脚本查询数据库的中间表（通过中间表脚本从原始表构建）
- 中间表脚本定义了中间表如何从原始表获取数据
- 转换时需要分析中间表脚本，理解原始表的结构和查询逻辑
- 结合两者生成直接查询原始表的新脚本，跳过中间表
- 支持任意两种数据库方言之间的转换（通过方言配置灵活指定）

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
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routers/             # 路由
│   │   ├── __init__.py
│   │   ├── visualization.py
│   │   ├── anonymization.py
│   │   ├── conversion.py
│   │   ├── validation.py
│   │   └── configuration.py
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
├── manage_db.py             # 数据库管理脚本
├── pyproject.toml           # 项目配置和依赖
├── README.md
└── .gitignore
```

## 功能模块

1. **中间表** - 管理和查看中间表脚本及可视化脚本
2. **匿名化** - 对脚本进行匿名化处理
3. **转换** - 核心转换功能，将中间表脚本转换为直接查询原始表的脚本
4. **验证** - 验证转换后的脚本正确性
5. **配置** - 系统配置管理（包括方言管理和 LLM 配置）

## 数据库设计

### 设计思路

本项目采用 SQLite 作为数据库，设计思路如下：

#### 1. 分层设计

- **方言层（dialects）**：存储支持的数据库方言，支持 MySQL、达梦、PostgreSQL、ORACLE、ODPS 等
- **任务层（tasks）**：针对可视化脚本的转换工作容器，通过三个字段关联方言表，灵活指定三个脚本的方言
- **业务数据层**：
  - `intermediate_scripts`（中间表脚本）：底层逻辑，独立存在，与任务无关
  - `visualization_scripts`（可视化脚本）：属于任务，通过字段关联中间表
- **配置层（configs）**：存储系统配置，包括 LLM 访问配置等

#### 2. 表关系设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              表关系图                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   dialects (方言表)                                                      │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │ 支持的方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS 等            │  │
│   │ 可通过 is_enabled 控制启用状态                                    │  │
│   │ 可通过 sort_order 控制显示顺序                                    │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│       ▲           ▲               ▲                                     │
│       │           │               │                                     │
│       └───────────┼───────────────┘                                     │
│                   │                                                       │
│   tasks (任务表) ◄──────────────────────────────────────────────────────│
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │ 新增三个方言字段：                                                │  │
│   │ - intermediate_dialect_id: 中间表脚本方言（关联 dialects）     │  │
│   │ - visualization_dialect_id: 可视化脚本方言（关联 dialects）   │  │
│   │ - converted_dialect_id: 转换后脚本方言（关联 dialects）       │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│       │                                                                   │
│       └──►  visualization_scripts (可视化脚本表)                        │
│                      │                                                   │
│                      └──►  (通过 intermediate_table_names 字段)         │
│                                    │                                      │
│                                    ▼                                      │
│   intermediate_scripts (中间脚本表) ◄──────────────────────────────────│
│   (独立存在，与任务无关)                                                  │
│                                                                         │
│   configs (配置表)                                                        │
│   (独立存在)                                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3. 关键设计决策

| 决策 | 说明 |
|------|------|
| **方言表独立存在** | 所有支持的数据库方言存储在方言表中，便于扩展和管理 |
| **任务表通过三个字段关联方言表** | 一次任务可灵活指定三个脚本的方言，具备高度扩展性 |
| **Task 只与 VisualizationScript 关联** | 任务是针对可视化脚本的转换工作，与中间表无关 |
| **IntermediateScript 独立存在** | 中间表是底层逻辑，可以被多个可视化脚本复用，不依赖任务 |
| **删除 Task 不影响 IntermediateScript** | 中间表独立存在，删除任务时不会级联删除中间表 |
| **intermediate_table_name 全局唯一** | 中间表名在整个系统中唯一，确保不会冲突 |
| **可视化脚本通过字段关联中间表** | 使用 `intermediate_table_names` 字段（逗号分隔），简化设计 |

#### 4. 约束设计

| 约束类型 | 应用场景 |
|----------|----------|
| 唯一约束 | 中间表名全局唯一；同一任务下可视化脚本名唯一；方言名唯一 |
| 外键约束 | visualization_scripts.task_id 关联 tasks.id，级联删除；tasks 的三个方言字段关联 dialects.id |

#### 5. 配置存储

- 采用键值对方式存储配置，灵活支持后续新增配置项
- 支持配置分类（category）和敏感配置标记（is_sensitive）
- 敏感配置（如 API Key）在存储时可以加密（当前版本明文存储，后续可增强）

### 表结构说明

#### 1. 方言表 (dialects)

**设计目的**：存储支持的数据库方言，使项目具备扩展性和实用性。

**关键特性**：
- 支持的方言包括：MySQL、达梦、PostgreSQL、ORACLE、ODPS 等
- 可通过 `is_enabled` 字段控制哪些方言可用
- 可通过 `sort_order` 字段控制方言显示顺序
- 任务表通过三个外键字段关联此表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | VARCHAR(100) | 方言英文名称（如：mysql, dameng, odps），唯一，必填 |
| display_name | VARCHAR(100) | 方言显示名称（如：MySQL, 达梦, ODPS），必填 |
| description | TEXT | 方言描述，可选 |
| is_enabled | INTEGER | 是否启用（1=是，0=否），默认 1 |
| sort_order | INTEGER | 排序顺序，默认 0 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**约束**：
- `UNIQUE (name)`：方言名全局唯一

**默认方言数据**：

| name | display_name | 说明 |
|------|--------------|------|
| mysql | MySQL | MySQL 数据库方言 |
| dameng | 达梦 | 达梦数据库方言 |
| postgresql | PostgreSQL | PostgreSQL 数据库方言 |
| oracle | ORACLE | Oracle 数据库方言 |
| odps | ODPS | 阿里云 ODPS (MaxCompute) 数据库方言 |

---

#### 2. 任务表 (tasks)

**设计目的**：作为针对可视化脚本的转换工作容器。

**关键特性**：
- 新增三个方言字段，支持灵活指定三个脚本的方言
- 创建任务时指定三个脚本的方言
- 任务只与可视化脚本相关，与中间表无关

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | VARCHAR(255) | 任务名，必填 |
| description | TEXT | 任务描述，可选 |
| intermediate_dialect_id | INTEGER | 中间表脚本方言ID，外键关联 dialects.id，可选 |
| visualization_dialect_id | INTEGER | 可视化脚本方言ID，外键关联 dialects.id，可选 |
| converted_dialect_id | INTEGER | 转换后脚本方言ID，外键关联 dialects.id，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**关系**：
- 一对多关联 `visualization_scripts`（可视化脚本）
- 多对一关联 `dialects`（通过三个方言字段）
- **与中间表无关联**

**重要说明**：
- 删除任务时，会级联删除关联的可视化脚本
- 删除任务时，**不会影响**中间表脚本

---

#### 3. 中间脚本表 (intermediate_scripts)

**设计目的**：存储中间表脚本，定义如何从原始表构建中间表。

**关键特性**：
- 中间表是**底层逻辑，独立存在**
- 与任务表**无关联**
- 删除任务时**不会影响**中间表
- 中间表名**全局唯一**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| intermediate_table_name | VARCHAR(255) | 中间表名，必填，**全局唯一** |
| script | TEXT | 中间表脚本（SQL），必填 |
| description | TEXT | 脚本描述，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**约束**：
- `UNIQUE (intermediate_table_name)`：中间表名全局唯一

**设计说明**：
- 中间表脚本定义了如何从原始表构建中间表
- 中间表可以被多个可视化脚本复用
- 中间表独立于任务存在，生命周期不受任务影响
- 中间表名全局唯一，确保系统中不会有重复的中间表

---

#### 4. 可视化脚本表 (visualization_scripts)

**设计目的**：存储可视化脚本，即查询中间表的 SQL 脚本。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| task_id | INTEGER | 外键，关联 tasks.id，级联删除 |
| name | VARCHAR(255) | 脚本名，必填 |
| intermediate_table_names | VARCHAR(1000) | 关联的中间表名，多个用逗号分隔（如 "table1,table2"） |
| visualization_script | TEXT | 可视化脚本（SQL），必填 |
| integrated_script | TEXT | 整合脚本（可视化脚本 + 中间表脚本） |
| anonymized_integrated_script | TEXT | 匿名化整合脚本 |
| converted_script | TEXT | 转换后新脚本（直接查询原始表） |
| description | TEXT | 脚本描述，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**约束**：
- `UNIQUE (task_id, name)`：同一个任务下，脚本名必须唯一
- `FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE`

**设计说明**：
- **重要变更**：不再使用多对多关联表，改用 `intermediate_table_names` 字段（逗号分隔）简化设计
- 设计原因：
  - 可视化脚本与中间表的关联相对简单，不需要复杂的多对多关系
  - 逗号分隔的方式更轻量，查询和维护更简单
  - 一个可视化脚本通常关联的中间表数量有限（一般 1-5 个），使用逗号分隔完全可以满足需求

---

#### 5. 配置表 (configs)

**设计目的**：存储系统配置项，包括 LLM 访问配置等。采用键值对方式，灵活支持后续新增配置项。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| config_key | VARCHAR(255) | 配置键，唯一，必填 |
| config_value | TEXT | 配置值 |
| description | TEXT | 配置描述 |
| category | VARCHAR(50) | 配置分类（如：llm, database, general） |
| is_sensitive | INTEGER | 是否为敏感配置（1=是，0=否），如 API Key |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**约束**：
- `UNIQUE (config_key)`：配置键必须唯一

**预定义配置项（LLM 相关）**：

| config_key | 默认值 | 说明 | 敏感 |
|------------|--------|------|------|
| llm.api_key | (空) | OpenAI 兼容 API 的访问密钥 | 是 |
| llm.api_base | (空) | API 基础地址（可选，用于兼容其他 API 服务） | 否 |
| llm.model_name | gpt-3.5-turbo | 使用的模型名称 | 否 |
| llm.temperature | 0.7 | 采样温度（0.0-2.0） | 否 |
| llm.max_tokens | 4096 | 最大生成 token 数 | 否 |

### 索引设计

为了提高查询性能，设计了以下索引：

| 表名 | 索引名 | 索引字段 |
|------|--------|----------|
| dialects | idx_dialects_name | name |
| dialects | idx_dialects_enabled | is_enabled |
| tasks | idx_tasks_name | name |
| tasks | idx_tasks_intermediate_dialect | intermediate_dialect_id |
| tasks | idx_tasks_visualization_dialect | visualization_dialect_id |
| tasks | idx_tasks_converted_dialect | converted_dialect_id |
| intermediate_scripts | idx_intermediate_scripts_table_name | intermediate_table_name |
| visualization_scripts | idx_visualization_scripts_task_id | task_id |
| visualization_scripts | idx_visualization_scripts_name | name |
| configs | idx_configs_key | config_key |
| configs | idx_configs_category | category |

### 触发器设计

为了自动更新 `updated_at` 字段，为每个表创建了更新触发器：

```sql
-- 示例：任务表更新触发器
CREATE TRIGGER update_tasks_updated_at 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

## 数据库管理

项目提供了 `manage_db.py` 脚本，用于管理数据库。

### 使用方法

```bash
# 初始化数据库（创建表结构，插入默认方言和配置）
uv run python manage_db.py init

# 清除所有数据（保留表结构，重置自增 ID）
uv run python manage_db.py clear

# 重置数据库（删除所有表并重新创建）
uv run python manage_db.py reset

# 查看数据库状态
uv run python manage_db.py status
```

### 命令说明

| 命令 | 说明 |
|------|------|
| init | 初始化数据库，创建表结构并插入默认方言数据和配置数据。如果数据库已存在，不会重复创建。 |
| clear | 清除所有表的数据，但保留表结构。执行前需要确认。 |
| reset | 重置数据库，删除所有表后重新创建。执行前需要确认。 |
| status | 查看数据库状态，包括表列表、记录数、字段信息、表关系图等。 |

### 重要提醒

- **方言表独立存在**：存储支持的数据库方言，包括 MySQL、达梦、PostgreSQL、ORACLE、ODPS 等
- **任务表通过三个方言字段关联方言表**：创建任务时可灵活指定三个脚本的方言
- **删除任务时**：只会级联删除关联的可视化脚本，**不会影响**中间表脚本
- **中间表是独立存在的**：可以被多个可视化脚本复用，生命周期不受任务影响
- **中间表名全局唯一**：确保系统中不会有重复的中间表名

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
# 方法1：使用管理脚本（推荐）
uv run python manage_db.py init

# 方法2：使用 Python 代码
uv run python -c "from app.database import init_db; init_db()"
```

**初始化后会自动插入**：
- 5 种默认方言：MySQL、达梦、PostgreSQL、ORACLE、ODPS
- LLM 默认配置项

### 配置 LLM（可选）

如果需要使用大模型进行智能转换，需要配置 LLM 相关参数：

1. 通过配置页面管理（推荐）
2. 或直接修改数据库 configs 表

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
- 数据库管理使用 manage_db.py 脚本

## 扩展性设计

### 方言扩展

如需添加新的数据库方言，只需向 `dialects` 表插入新记录：

```sql
-- 示例：添加 SQL Server 方言
INSERT INTO dialects (name, display_name, description, is_enabled, sort_order) 
VALUES ('sqlserver', 'SQL Server', 'Microsoft SQL Server 数据库方言', 1, 6);
```

### 任务创建时指定方言

创建任务时，可以灵活指定三个脚本的方言：

| 字段 | 说明 |
|------|------|
| intermediate_dialect_id | 中间表脚本使用的方言 |
| visualization_dialect_id | 可视化脚本使用的方言 |
| converted_dialect_id | 转换后脚本使用的方言 |

这样设计使得项目支持任意两种数据库方言之间的转换，具备高度的扩展性和实用性。

## 许可证

MIT License
