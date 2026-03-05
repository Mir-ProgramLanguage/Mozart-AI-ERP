"""
原生AI ERP架构设计

核心理念：
1. 用户不需要知道"采购"、"销售"等概念
2. 用户只需要说"我做了什么"或"我想知道什么"
3. AI负责理解、分类、存储和检索

数据流：
输入 → AI理解 → 事件存储 → AI查询 → 输出
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from app.database import Base


class BusinessEvent(Base):
    """
    业务事件表 - 核心数据模型

    这不是传统的"采购表"或"销售表"，而是一个统一的事件流
    所有业务活动都记录为事件，AI负责理解和分类
    """
    __tablename__ = "business_events"

    id = Column(Integer, primary_key=True, index=True)

    # 用户信息
    user_id = Column(Integer, index=True)

    # 原始输入（保留用户的原始表达）
    raw_input = Column(Text, nullable=False, comment="用户的原始输入")
    input_type = Column(String(20), comment="输入类型: text/voice/image")
    input_file_url = Column(String(500), comment="如果是图片/语音，存储文件URL")

    # AI理解结果
    intent = Column(String(50), index=True, comment="AI识别的意图: purchase/sales/expense/query等")
    confidence = Column(DECIMAL(3, 2), comment="AI识别的置信度 0-1")

    # AI提取的结构化数据（JSONB - 灵活存储）
    extracted_data = Column(JSON, comment="AI提取的结构化信息")

    # 元数据
    event_date = Column(DateTime, index=True, comment="事件发生日期")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 审核状态
    status = Column(String(20), default="pending", comment="pending/approved/rejected")
    reviewed_by = Column(Integer, comment="审核人ID")
    reviewed_at = Column(DateTime, comment="审核时间")

    # 备注
    notes = Column(Text, comment="用户或系统备注")


class AIQueryHistory(Base):
    """
    AI查询历史表

    记录用户的自然语言查询和AI的回答
    """
    __tablename__ = "ai_query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)

    # 用户查询
    query_text = Column(Text, nullable=False, comment="用户的自然语言查询")
    query_intent = Column(String(50), comment="查询意图分类")

    # AI响应
    response_text = Column(Text, comment="AI的回答")
    retrieved_events = Column(JSON, comment="检索到的相关事件ID列表")

    # 性能指标
    response_time_ms = Column(Integer, comment="响应时间（毫秒）")

    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    """用户表 - 保持简单"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
