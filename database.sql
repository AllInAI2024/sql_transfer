-- SQL脚本转换工具数据库初始化脚本
-- 数据库类型: SQLite
-- 创建日期: 2026-04-19
-- 版本: 2.0

-- ============================================
-- 数据库设计思路
-- ============================================
-- 
-- 1. 任务表 (tasks)
--    - 任务是转换工作的顶层容器
--    - 每个任务可以包含多个中间表脚本和多个可视化脚本
--    - 通过任务可以统一管理一组相关的脚本转换工作
-- 
-- 2. 中间脚本表 (intermediate_scripts)
--    - 中间表脚本定义了如何从 ODPS 原始表构建达梦数据库的中间表
--    - 每个中间表脚本对应一个唯一的中间表名（在同一个任务下）
--    - 添加唯一约束：同一个任务下，中间表名必须唯一
--    - 与任务表通过 task_id 建立外键关联
-- 
-- 3. 可视化脚本表 (visualization_scripts)
--    - 可视化脚本是查询达梦数据库中间表的 SQL 脚本
--    - 每个可视化脚本需要关联一个或多个中间表
--    - 设计变更：不再使用多对多关联表，改用 intermediate_table_names 字段（逗号分隔）
--    - 添加唯一约束：同一个任务下，脚本名必须唯一
--    - 与任务表通过 task_id 建立外键关联
-- 
-- 4. 配置表 (configs)
--    - 使用键值对方式存储系统配置
--    - 灵活支持后续新增配置项
--    - 支持配置分类和敏感配置标记
--    - 主要用于存储 LLM 访问配置（API Key, Base URL, Model Name 等）
-- 
-- ============================================


-- ============================================
-- 任务表 (tasks)
-- 转换之前先创建任务，每个任务包括多个 sql 脚本
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 为任务表创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_name ON tasks(name);


-- ============================================
-- 中间脚本表 (intermediate_scripts)
-- 保存中间表脚本
-- 
-- 设计说明：
-- - 每个中间表脚本对应一个唯一的中间表名（在同一个任务下）
-- - 添加唯一约束 uq_intermediate_script_task_table
-- - task_id 是外键，关联 tasks 表
-- ============================================
CREATE TABLE IF NOT EXISTS intermediate_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    intermediate_table_name VARCHAR(255) NOT NULL,
    script TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE (task_id, intermediate_table_name)
);

-- 为中间脚本表创建索引
CREATE INDEX IF NOT EXISTS idx_intermediate_scripts_task_id ON intermediate_scripts(task_id);
CREATE INDEX IF NOT EXISTS idx_intermediate_scripts_table_name ON intermediate_scripts(intermediate_table_name);


-- ============================================
-- 可视化脚本表 (visualization_scripts)
-- 保存可视化脚本
-- 
-- 设计说明：
-- - 每个可视化脚本需要关联一个或多个中间表
-- - 设计变更：不再使用多对多关联表，改用 intermediate_table_names 字段（逗号分隔）
-- - 例如：intermediate_table_names = "table1,table2,table3"
-- - 添加唯一约束 uq_visualization_script_task_name
-- - task_id 是外键，关联 tasks 表
-- 
-- 字段说明：
-- - intermediate_table_names: 关联的中间表名，多个用逗号分隔
-- - integrated_script: 整合脚本（把该可视化脚本和对应的中间表脚本整合成一个脚本）
-- - anonymized_integrated_script: 匿名化整合脚本
-- - converted_script: 转换后新脚本（直接查询 ODPS 原始表的脚本）
-- ============================================
CREATE TABLE IF NOT EXISTS visualization_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    intermediate_table_names VARCHAR(1000),
    visualization_script TEXT NOT NULL,
    integrated_script TEXT,
    anonymized_integrated_script TEXT,
    converted_script TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE (task_id, name)
);

-- 为可视化脚本表创建索引
CREATE INDEX IF NOT EXISTS idx_visualization_scripts_task_id ON visualization_scripts(task_id);
CREATE INDEX IF NOT EXISTS idx_visualization_scripts_name ON visualization_scripts(name);


-- ============================================
-- 配置表 (configs)
-- 存储系统配置项，包括 LLM 访问配置等
-- 
-- 设计说明：
-- - 使用键值对方式存储配置，灵活支持后续新增配置项
-- - config_key 是唯一的，确保同一个配置项不会重复
-- - 支持配置分类（category），便于管理
-- - 支持敏感配置标记（is_sensitive），如 API Key
-- - 所有配置都有描述字段，便于理解配置用途
-- 
-- 配置项示例：
-- - llm.api_key: OpenAI 兼容 API 的密钥（敏感配置）
-- - llm.api_base: API 基础地址（可选，用于兼容其他 API）
-- - llm.model_name: 使用的模型名称
-- - llm.temperature: 采样温度（可选）
-- - llm.max_tokens: 最大生成 token 数（可选）
-- ============================================
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    category VARCHAR(50),
    is_sensitive INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 为配置表创建索引
CREATE INDEX IF NOT EXISTS idx_configs_key ON configs(config_key);
CREATE INDEX IF NOT EXISTS idx_configs_category ON configs(category);


-- ============================================
-- 创建触发器来自动更新 updated_at 字段
-- ============================================

-- 任务表更新触发器
CREATE TRIGGER IF NOT EXISTS update_tasks_updated_at 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 中间脚本表更新触发器
CREATE TRIGGER IF NOT EXISTS update_intermediate_scripts_updated_at 
AFTER UPDATE ON intermediate_scripts
BEGIN
    UPDATE intermediate_scripts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 可视化脚本表更新触发器
CREATE TRIGGER IF NOT EXISTS update_visualization_scripts_updated_at 
AFTER UPDATE ON visualization_scripts
BEGIN
    UPDATE visualization_scripts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 配置表更新触发器
CREATE TRIGGER IF NOT EXISTS update_configs_updated_at 
AFTER UPDATE ON configs
BEGIN
    UPDATE configs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;


-- ============================================
-- 插入默认配置数据（LLM 配置模板）
-- ============================================

-- LLM API 密钥（敏感配置）
INSERT OR IGNORE INTO configs (config_key, config_value, description, category, is_sensitive) 
VALUES (
    'llm.api_key', 
    '', 
    'OpenAI 兼容 API 的访问密钥', 
    'llm', 
    1
);

-- LLM API 基础地址（可选）
INSERT OR IGNORE INTO configs (config_key, config_value, description, category, is_sensitive) 
VALUES (
    'llm.api_base', 
    '', 
    'API 基础地址（可选，用于兼容其他 API 服务，如：https://api.openai.com/v1）', 
    'llm', 
    0
);

-- LLM 模型名称
INSERT OR IGNORE INTO configs (config_key, config_value, description, category, is_sensitive) 
VALUES (
    'llm.model_name', 
    'gpt-3.5-turbo', 
    '使用的模型名称', 
    'llm', 
    0
);

-- LLM 采样温度
INSERT OR IGNORE INTO configs (config_key, config_value, description, category, is_sensitive) 
VALUES (
    'llm.temperature', 
    '0.7', 
    '采样温度（0.0-2.0，越低越确定，越高越随机）', 
    'llm', 
    0
);

-- LLM 最大生成 token 数
INSERT OR IGNORE INTO configs (config_key, config_value, description, category, is_sensitive) 
VALUES (
    'llm.max_tokens', 
    '4096', 
    '最大生成 token 数', 
    'llm', 
    0
);


-- ============================================
-- 数据库初始化完成
-- ============================================
PRINT '数据库初始化完成！';
PRINT '表结构：tasks, intermediate_scripts, visualization_scripts, configs';
PRINT '默认配置已插入，请在配置页面修改 LLM 相关设置。';
