from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Task(Base):
    """
    任务表
    - 转换之前先创建任务，每个任务针对一个可视化脚本
    
    设计思路：
    - 任务是针对可视化脚本的转换工作容器
    - 每个任务包含一个可视化脚本
    - 任务只与可视化脚本相关，与中间表无关
    - 通过任务可以统一管理可视化脚本的转换工作
    """
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="任务名")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="任务描述")
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        comment="修改时间"
    )
    
    # 关系：任务只与可视化脚本相关，与中间表无关
    visualization_scripts: Mapped[List["VisualizationScript"]] = relationship(
        "VisualizationScript", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}')>"


class IntermediateScript(Base):
    """
    中间脚本表
    - 保存中间表脚本
    
    设计思路：
    - 中间表脚本定义了如何从 ODPS 原始表构建达梦数据库的中间表
    - 中间表是底层逻辑，独立存在，与任务无关
    - intermediate_table_name 全局唯一，确保系统中不会有重复的中间表名
    - 与任务表无关联，删除任务时不会影响中间表
    """
    __tablename__ = "intermediate_scripts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    intermediate_table_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        unique=True,
        comment="中间表名（全局唯一）"
    )
    script: Mapped[str] = mapped_column(Text, nullable=False, comment="中间表脚本")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="脚本描述")
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        comment="修改时间"
    )
    
    # 注意：中间表与任务无关联，独立存在
    
    def __repr__(self):
        return f"<IntermediateScript(id={self.id}, intermediate_table_name='{self.intermediate_table_name}')>"


class VisualizationScript(Base):
    """
    可视化脚本表
    - 保存可视化脚本
    
    设计思路：
    - 可视化脚本是查询达梦数据库中间表的 SQL 脚本
    - 每个可视化脚本属于一个任务
    - 每个可视化脚本需要关联一个或多个中间表（通过 intermediate_table_names 字段，逗号分隔）
    - 不再使用多对多关联表，简化设计
    - name 添加唯一约束，确保同一个任务下不会有重复的脚本名
    - 与任务表通过 task_id 建立外键关联
    
    字段说明：
    - intermediate_table_names: 关联的中间表名，多个用逗号分隔（如 "table1,table2,table3"）
    - integrated_script: 整合脚本（把该可视化脚本和对应的中间表脚本整合成一个脚本）
    - anonymized_integrated_script: 匿名化整合脚本
    - converted_script: 转换后新脚本（直接查询 ODPS 原始表的脚本）
    """
    __tablename__ = "visualization_scripts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="所属任务ID"
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="脚本名")
    
    # 关联的中间表名，多个用逗号分隔
    intermediate_table_names: Mapped[Optional[str]] = mapped_column(
        String(1000), 
        nullable=True,
        comment="关联的中间表名，多个用逗号分隔"
    )
    
    visualization_script: Mapped[str] = mapped_column(Text, nullable=False, comment="可视化脚本")
    
    # 整合后的脚本
    integrated_script: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="整合脚本（把该可视化脚本和对应的中间表脚本整合成一个脚本）"
    )
    anonymized_integrated_script: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="匿名化整合脚本"
    )
    converted_script: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="转换后新脚本"
    )
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="脚本描述")
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        comment="修改时间"
    )
    
    # 唯一约束：同一个任务下，脚本名必须唯一
    __table_args__ = (
        UniqueConstraint('task_id', 'name', name='uq_visualization_script_task_name'),
    )
    
    # 关系
    task: Mapped["Task"] = relationship("Task", back_populates="visualization_scripts")
    
    @property
    def intermediate_table_name_list(self) -> List[str]:
        """
        获取所有关联的中间表名列表
        """
        if not self.intermediate_table_names:
            return []
        return [name.strip() for name in self.intermediate_table_names.split(',') if name.strip()]
    
    def set_intermediate_table_names(self, names: List[str]) -> None:
        """
        设置关联的中间表名
        """
        self.intermediate_table_names = ','.join([name.strip() for name in names if name.strip()])
    
    def __repr__(self):
        return f"<VisualizationScript(id={self.id}, name='{self.name}')>"


class Config(Base):
    """
    配置表
    - 存储系统配置项，包括 LLM 访问配置等
    
    设计思路：
    - 使用键值对方式存储配置，灵活支持后续新增配置项
    - config_key 是唯一的，确保同一个配置项不会重复
    - 敏感信息（如 API Key）可以加密存储（当前版本明文存储，后续可增强）
    - 所有配置都有描述字段，便于理解配置用途
    
    配置项分类：
    1. LLM 相关配置：
       - llm.api_key: OpenAI 兼容 API 的密钥
       - llm.api_base: API 基础地址（可选，用于兼容其他 API）
       - llm.model_name: 使用的模型名称
       - llm.temperature: 采样温度（可选）
       - llm.max_tokens: 最大生成 token 数（可选）
    
    2. 其他业务配置（后续扩展）：
       - 数据库连接配置
       - SSE 相关配置
       - 其他业务参数
    """
    __tablename__ = "configs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True,
        index=True,
        comment="配置键"
    )
    config_value: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="配置值"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="配置描述"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        index=True,
        comment="配置分类（如：llm, database, general）"
    )
    is_sensitive: Mapped[bool] = mapped_column(
        default=False,
        comment="是否为敏感配置（如 API Key）"
    )
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        comment="修改时间"
    )
    
    def __repr__(self):
        return f"<Config(id={self.id}, config_key='{self.config_key}')>"
