-- SQL脚本转换工具数据库初始化脚本
-- 数据库类型: SQLite
-- 创建日期: 2026-04-19

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
-- ============================================
CREATE TABLE IF NOT EXISTS intermediate_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    intermediate_table_name VARCHAR(255) NOT NULL,
    script TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 为中间脚本表创建索引
CREATE INDEX IF NOT EXISTS idx_intermediate_scripts_task_id ON intermediate_scripts(task_id);
CREATE INDEX IF NOT EXISTS idx_intermediate_scripts_table_name ON intermediate_scripts(intermediate_table_name);

-- ============================================
-- 可视化脚本表 (visualization_scripts)
-- 保存可视化脚本
-- ============================================
CREATE TABLE IF NOT EXISTS visualization_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    visualization_script TEXT NOT NULL,
    integrated_script TEXT,
    anonymized_integrated_script TEXT,
    converted_script TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 为可视化脚本表创建索引
CREATE INDEX IF NOT EXISTS idx_visualization_scripts_task_id ON visualization_scripts(task_id);
CREATE INDEX IF NOT EXISTS idx_visualization_scripts_name ON visualization_scripts(name);

-- ============================================
-- 可视化脚本与中间表的关联表 (visualization_intermediate)
-- 多对多关系表
-- ============================================
CREATE TABLE IF NOT EXISTS visualization_intermediate (
    visualization_script_id INTEGER NOT NULL,
    intermediate_script_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (visualization_script_id, intermediate_script_id),
    FOREIGN KEY (visualization_script_id) REFERENCES visualization_scripts(id) ON DELETE CASCADE,
    FOREIGN KEY (intermediate_script_id) REFERENCES intermediate_scripts(id) ON DELETE CASCADE
);

-- 为关联表创建索引
CREATE INDEX IF NOT EXISTS idx_visualization_intermediate_vs_id ON visualization_intermediate(visualization_script_id);
CREATE INDEX IF NOT EXISTS idx_visualization_intermediate_is_id ON visualization_intermediate(intermediate_script_id);

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

-- ============================================
-- 插入示例数据（可选）
-- ============================================

-- 示例任务
-- INSERT INTO tasks (name, description) VALUES 
-- ('示例转换任务', '用于测试SQL脚本转换功能的示例任务');

-- 示例中间脚本
-- INSERT INTO intermediate_scripts (task_id, intermediate_table_name, script, description) VALUES 
-- (1, 'user_summary', 'CREATE TABLE user_summary AS SELECT user_id, COUNT(*) as order_count FROM orders GROUP BY user_id;', '用户汇总中间表脚本');

-- 示例可视化脚本
-- INSERT INTO visualization_scripts (task_id, name, visualization_script, description) VALUES 
-- (1, '用户订单统计', 'SELECT * FROM user_summary WHERE order_count > 10;', '统计订单数超过10的用户');

-- 示例关联关系
-- INSERT INTO visualization_intermediate (visualization_script_id, intermediate_script_id) VALUES 
-- (1, 1);

-- ============================================
-- 数据库初始化完成
-- ============================================
PRINT '数据库初始化完成！';
