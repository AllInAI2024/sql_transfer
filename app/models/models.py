from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# 可视化脚本与中间表的关联表（多对多关系）
visualization_intermediate_association = Table(
    'visualization_intermediate',
    Base.metadata,
    Column('visualization_script_id', Integer, ForeignKey('visualization_scripts.id'), primary_key=True),
    Column('intermediate_script_id', Integer, ForeignKey('intermediate_scripts.id'), primary_key=True)
)


class Task(Base):
    """
    任务表
    - 转换之前先创建任务，每个任务包括多个 sql 脚本
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
    
    # 关系
    intermediate_scripts: Mapped[List["IntermediateScript"]] = relationship(
        "IntermediateScript", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
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
    """
    __tablename__ = "intermediate_scripts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True,
        comment="所属任务ID"
    )
    intermediate_table_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        comment="中间表名"
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
    
    # 关系
    task: Mapped["Task"] = relationship("Task", back_populates="intermediate_scripts")
    visualization_scripts: Mapped[List["VisualizationScript"]] = relationship(
        "VisualizationScript",
        secondary=visualization_intermediate_association,
        back_populates="intermediate_scripts"
    )
    
    def __repr__(self):
        return f"<IntermediateScript(id={self.id}, intermediate_table_name='{self.intermediate_table_name}')>"


class VisualizationScript(Base):
    """
    可视化脚本表
    - 保存可视化脚本
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
    
    # 关系
    task: Mapped["Task"] = relationship("Task", back_populates="visualization_scripts")
    intermediate_scripts: Mapped[List["IntermediateScript"]] = relationship(
        "IntermediateScript",
        secondary=visualization_intermediate_association,
        back_populates="visualization_scripts"
    )
    
    @property
    def intermediate_table_names(self) -> List[str]:
        """
        获取所有关联的中间表名
        """
        return [script.intermediate_table_name for script in self.intermediate_scripts]
    
    def __repr__(self):
        return f"<VisualizationScript(id={self.id}, name='{self.name}')>"
