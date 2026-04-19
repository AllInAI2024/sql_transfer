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

1. **可视化脚本** - 管理和查看可视化脚本
2. **匿名化** - 对脚本进行匿名化处理
3. **脚本转换** - 核心转换功能，将中间表脚本转换为直接查询 ODPS 的脚本
4. **验证** - 验证转换后的脚本正确性
5. **配置** - 系统配置管理

## 数据库设计

### 设计思路

本项目采用 SQLite 作为数据库，设计思路如下：

1. **分层设计**：
   - 任务层（tasks）：作为顶层容器，统一管理一组相关的脚本转换工作
   - 业务数据层（intermediate_scripts, visualization_scripts）：存储核心业务数据
   - 配置层（configs）：存储系统配置，包括 LLM 访问配置等

2. **关系设计**：
   - 任务与脚本：一对多关系（一个任务包含多个中间表脚本和多个可视化脚本）
   - 脚本关联：可视化脚本通过 `intermediate_table_names` 字段（逗号分隔）关联一个或多个中间表名

3. **约束设计**：
   - 唯一约束：同一任务下，中间表名和可视化脚本名必须唯一
   - 外键约束：确保数据完整性，级联删除

4. **配置存储**：
   - 采用键值对方式存储配置，灵活支持后续新增配置项
   - 支持配置分类和敏感配置标记
   - 敏感配置（如 API Key）在存储时可以加密（当前版本明文存储，后续可增强）

### 表结构说明

#### 1. 任务表 (tasks)

**设计目的**：作为转换工作的顶层容器，统一管理一组相关的脚本转换工作。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | VARCHAR(255) | 任务名，必填 |
| description | TEXT | 任务描述，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**关系**：
- 一对多关联 intermediate_scripts（中间表脚本）
- 一对多关联 visualization_scripts（可视化脚本）

---

#### 2. 中间脚本表 (intermediate_scripts)

**设计目的**：存储中间表脚本，定义如何从 ODPS 原始表构建达梦数据库的中间表。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| task_id | INTEGER | 外键，关联 tasks.id，级联删除 |
| intermediate_table_name | VARCHAR(255) | 中间表名，必填 |
| script | TEXT | 中间表脚本（SQL），必填 |
| description | TEXT | 脚本描述，可选 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 修改时间 |

**约束**：
- `UNIQUE (task_id, intermediate_table_name)`：同一个任务下，中间表名必须唯一
- `FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE`

**设计说明**：
- 中间表名添加唯一约束，确保同一个任务下不会有重复的中间表名
- 通过 task_id 与任务表建立外键关联
- 当任务删除时，相关的中间表脚本会级联删除

---

#### 3. 可视化脚本表 (visualization_scripts)

**设计目的**：存储可视化脚本，即查询达梦数据库中间表的 SQL 脚本。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| task_id | INTEGER | 外键，关联 tasks.id，级联删除 |
| name | VARCHAR(255) | 脚本名，必填 |
| intermediate_table_names | VARCHAR(1000) | 关联的中间表名，多个用逗号分隔（如 "table1,table2"） |
| visualization_script | TEXT | 可视化脚本（SQL），必填 |
| integrated_script | TEXT | 整合脚本（可视化脚本 + 中间表脚本） |
| anonymized_integrated_script | TEXT | 匿名化整合脚本 |
| converted_script | TEXT | 转换后新脚本（直接查询 ODPS 原始表） |
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
- 使用示例：
  ```python
  # 设置中间表名
  script.set_intermediate_table_names(["user_summary", "order_summary"])
  # 结果: intermediate_table_names = "user_summary,order_summary"
  
  # 获取中间表名列表
  names = script.intermediate_table_name_list
  # 结果: ["user_summary", "order_summary"]
  ```

---

#### 4. 配置表 (configs)

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

**设计说明**：
- 使用键值对方式存储配置，无需修改表结构即可新增配置项
- 支持配置分类，便于按类别管理配置
- 支持敏感配置标记，API Key 等敏感信息可以加密存储（当前版本明文存储）
- 配置项可以通过配置页面进行管理

### 索引设计

为了提高查询性能，设计了以下索引：

| 表名 | 索引名 | 索引字段 |
|------|--------|----------|
| tasks | idx_tasks_name | name |
| intermediate_scripts | idx_intermediate_scripts_task_id | task_id |
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
# 初始化数据库（创建表结构，插入默认配置）
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
| init | 初始化数据库，创建表结构并插入默认配置数据。如果数据库已存在，不会重复创建。 |
| clear | 清除所有表的数据，但保留表结构。执行前需要确认。 |
| reset | 重置数据库，删除所有表后重新创建。执行前需要确认。 |
| status | 查看数据库状态，包括表列表、记录数、字段信息等。 |

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

## 许可证

MIT License
