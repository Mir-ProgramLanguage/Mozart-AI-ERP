"""
数据模型 - Actor, Event, Reward

整合能力图谱、贡献评估、回报系统
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, DECIMAL, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class ActorType:
    """Actor类型常量"""
    HUMAN = "human"          # 真实员工
    AI_AGENT = "ai_agent"   # 虚拟AI员工
    EXTERNAL = "external"    # 外部合作者


class Actor(Base):
    """
    参与者模型（能力个体）
    
    核心概念：
    - 不是"员工"，是"能力集合"
    - 可以有多种能力，可以自由切换角色
    - 贡献越多，能力越强，回报越多
    - 支持真实员工(HUMAN)、虚拟AI员工(AI_AGENT)、外部合作者(EXTERNAL)
    """
    
    __tablename__ = "actors"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(50), unique=True, nullable=False)  # 匿名代号
    
    # ⭐ Actor类型：human(真实员工) / ai_agent(虚拟AI员工) / external(外部合作者)
    actor_type = Column(String(20), default=ActorType.HUMAN, index=True)
    
    # 关联的用户ID（如果是真实员工）
    user_id = Column(Integer, index=True)
    
    # ⭐ 虚拟AI员工配置（仅AI_AGENT类型使用）
    ai_config = Column(JSON, default=dict)  # {
        # "role": "AI助手",
        # "description": "擅长文案撰写",
        # "capabilities": ["文案", "分析", "整理"],
        # "system_prompt": "你是公司的AI助手...",
        # "model": "deepseek",
        # "temperature": 0.7
        # }
    
    # ⭐ 能力图谱（多维度）
    capabilities = Column(JSON, default=dict)  # {"开发": 0.9, "产品": 0.8, ...}
    capability_history = Column(JSON, default=list)  # 成长历史
    
    # ⭐ 贡献记录
    total_contributions = Column(DECIMAL(12, 2), default=0)  # 总贡献值
    contributions_by_type = Column(JSON, default=dict)  # 分类贡献
    contribution_count = Column(Integer, default=0)  # 贡献次数
    
    # ⭐ 回报记录
    total_rewards = Column(DECIMAL(12, 2), default=0)  # 总回报
    available_rewards = Column(DECIMAL(12, 2), default=0)  # 可兑现回报
    reward_history = Column(JSON, default=list)  # 回报历史
    
    # 信任与声誉
    trust_score = Column(DECIMAL(3, 2), default=0.5)  # 信任分数
    reputation_score = Column(DECIMAL(3, 2), default=0.5)  # 声誉分数
    
    # 工作状态
    current_tasks = Column(JSON, default=list)  # 当前任务ID列表
    availability = Column(DECIMAL(3, 2), default=1.0)  # 可投入度
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime, server_default=func.now())
    
    def to_dict(self, include_ai_config=False):
        """转换为字典"""
        result = {
            "id": str(self.id),
            "display_name": self.display_name,
            "actor_type": self.actor_type,
            "user_id": self.user_id,
            "capabilities": self.capabilities,
            "total_contributions": float(self.total_contributions) if self.total_contributions else 0,
            "contributions_by_type": self.contributions_by_type or {},
            "total_rewards": float(self.total_rewards) if self.total_rewards else 0,
            "available_rewards": float(self.available_rewards) if self.available_rewards else 0,
            "trust_score": float(self.trust_score) if self.trust_score else 0.5,
            "reputation_score": float(self.reputation_score) if self.reputation_score else 0.5,
            "availability": float(self.availability) if self.availability else 1.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None
        }
        # AI配置仅在明确请求时返回（安全性）
        if include_ai_config and self.actor_type == ActorType.AI_AGENT:
            result["ai_config"] = self.ai_config
        return result


class Event(Base):
    """
    事件模型（贡献事件）
    
    核心概念：
    - 所有事件都是贡献
    - 每个贡献都有价值
    - AI自动评估价值
    """
    
    __tablename__ = "events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # 事件内容
    action = Column(String(50), nullable=False)  # say/contribute/approve/...
    content = Column(String, nullable=False)
    attachments = Column(JSON, default=list)
    
    # AI理解
    ai_analysis = Column(JSON, default=dict)
    
    # ⭐⭐⭐ 贡献评估（核心）
    contribution_type = Column(String(50), index=True)  # 贡献类型
    contribution_status = Column(String(20), default="pending", index=True)  # pending/verified/rejected
    contribution_value = Column(DECIMAL(12, 2))  # 预估贡献价值
    value_confidence = Column(DECIMAL(3, 2))  # 价值置信度
    
    # ⭐ 实际价值
    actual_value = Column(DECIMAL(12, 2))  # 实际实现的价值
    value_realized_at = Column(DateTime)  # 价值实现时间
    
    # ⭐ 价值计算依据
    value_calculation = Column(JSON, default=dict)  # 计算过程
    
    # 关联
    related_events = Column(JSON, default=list)  # 使用JSON兼容SQLite
    related_tasks = Column(JSON, default=list)
    beneficiaries = Column(JSON, default=list)  # 受益方
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), index=True)
    verified_at = Column(DateTime)  # 验证时间
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "actor_id": str(self.actor_id),
            "action": self.action,
            "content": self.content,
            "contribution_type": self.contribution_type,
            "contribution_status": self.contribution_status,
            "contribution_value": float(self.contribution_value) if self.contribution_value else None,
            "actual_value": float(self.actual_value) if self.actual_value else None,
            "value_calculation": self.value_calculation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None
        }


class Reward(Base):
    """
    回报模型
    
    核心概念：
    - 贡献值转换为回报
    - 多种回报类型
    - 可选择兑现方式
    """
    
    __tablename__ = "rewards"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    
    # 回报信息
    reward_type = Column(String(50), nullable=False)  # cash_bonus/profit_sharing/...
    amount = Column(DECIMAL(12, 2), nullable=False)  # 回报金额
    contribution_type = Column(String(50))  # 来源贡献类型
    
    # 状态
    status = Column(String(20), default="pending", index=True)  # pending/claimed/claimed
    
    # 时间
    created_at = Column(DateTime, server_default=func.now())
    claimed_at = Column(DateTime)  # 兑现时间
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "actor_id": str(self.actor_id),
            "event_id": str(self.event_id),
            "reward_type": self.reward_type,
            "amount": float(self.amount),
            "contribution_type": self.contribution_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None
        }


class Task(Base):
    """
    任务模型
    
    核心概念：
    - AI生成任务
    - 智能分配
    - 完成任务也是贡献
    """
    
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 任务信息
    type = Column(String(50), nullable=False)  # verify/approve/execute/...
    description = Column(String, nullable=False)
    priority = Column(Integer, default=50)  # 优先级 0-100
    
    # 分配
    assigned_to = Column(JSON, default=list)  # 可能多人，使用JSON兼容SQLite
    status = Column(String(20), default="pending", index=True)
    
    # 关联
    related_events = Column(JSON, default=list)
    
    # 时间
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    deadline = Column(DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "type": self.type,
            "description": self.description,
            "priority": self.priority,
            "assigned_to": [str(uid) for uid in self.assigned_to] if self.assigned_to else [],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class ActorInteraction(Base):
    """
    Actor交互记录模型
    
    记录真实员工与虚拟AI员工之间的对话、任务请求、协作等交互
    """
    
    __tablename__ = "actor_interactions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 交互类型
    interaction_type = Column(String(30), nullable=False, index=True)  # 
    # chat: 对话
    # task_request: 任务请求
    # ai_collaboration: AI协作
    # approval: 审批
    
    # 发起者
    from_actor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    from_actor_name = Column(String(50))  # 缓存显示名
    
    # 接收者（可能是真实员工或AI员工）
    to_actor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    to_actor_name = Column(String(50))  # 缓存显示名
    
    # 交互内容
    message = Column(Text, nullable=False)  # 原始消息
    context = Column(JSON, default=dict)  # 上下文信息
    
    # AI处理结果
    ai_response = Column(Text)  # AI的回复
    task_id = Column(UUID(as_uuid=True))  # 如果产生了任务
    events_created = Column(JSON, default=list)  # 产生的事件，使用JSON兼容SQLite
    
    # 状态
    status = Column(String(20), default="pending", index=True)  # pending/completed/failed
    
    # 时间
    created_at = Column(DateTime, server_default=func.now(), index=True)
    completed_at = Column(DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "interaction_type": self.interaction_type,
            "from_actor_id": str(self.from_actor_id),
            "from_actor_name": self.from_actor_name,
            "to_actor_id": str(self.to_actor_id),
            "to_actor_name": self.to_actor_name,
            "message": self.message,
            "ai_response": self.ai_response,
            "task_id": str(self.task_id) if self.task_id else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


# 枚举类型
class InteractionType:
    """交互类型"""
    CHAT = "chat"              # 对话
    TASK_REQUEST = "task_request"  # 任务请求
    AI_COLLABORATION = "ai_collaboration"  # AI协作
    APPROVAL = "approval"     # 审批


class InteractionStatus:
    """交互状态"""
    PENDING = "pending"        # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class RewardType:
    """回报类型"""
    CASH_BONUS = "cash_bonus"              # 现金奖励
    PROFIT_SHARING = "profit_sharing"      # 利润分红
    STOCK_OPTIONS = "stock_options"        # 期权激励
    SKILL_POINTS = "skill_points"          # 技能点


class RewardStatus:
    """回报状态"""
    PENDING = "pending"      # 待兑现
    CLAIMED = "claimed"      # 已兑现
    EXPIRED = "expired"      # 已过期


class ContributionStatus:
    """贡献状态"""
    PENDING = "pending"      # 待验证
    VERIFIED = "verified"    # 已验证
    REJECTED = "rejected"    # 已拒绝
