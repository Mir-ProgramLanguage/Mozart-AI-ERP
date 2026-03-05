"""
贡献系统 API

核心接口：
- POST /api/contribute - 提交贡献
- GET /api/my/contributions - 获取我的贡献
- POST /api/contributions/{id}/verify - 验证贡献
- GET /api/my/rewards - 获取我的回报
- POST /api/rewards/{id}/claim - 兑现回报
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.contribution import (
    Actor, Event, Reward, Task,
    ContributionStatus, RewardStatus, ActorType
)
from app.services.contribution_evaluator import ContributionEvaluator
from app.services.reward_calculator import RewardCalculator


router = APIRouter()


# ============ 请求模型 ============

class ContributeRequest(BaseModel):
    """提交贡献请求"""
    content: str = Field(..., description="贡献内容描述")
    contribution_type: Optional[str] = Field(None, description="贡献类型")
    details: Optional[dict] = Field(default={}, description="详细信息")


class VerifyContributionRequest(BaseModel):
    """验证贡献请求"""
    actual_value: float = Field(..., description="实际价值")
    verifier_note: Optional[str] = Field("", description="验证备注")


class ClaimRewardRequest(BaseModel):
    """兑现回报请求"""
    amount: Optional[float] = Field(None, description="兑现金额（可选，默认全部）")


# ============ 响应模型 ============

class ContributionResponse(BaseModel):
    """贡献响应"""
    id: str
    content: str
    contribution_type: Optional[str]
    contribution_status: str
    estimated_value: Optional[float]
    actual_value: Optional[float]
    created_at: str


class RewardResponse(BaseModel):
    """回报响应"""
    id: str
    reward_type: str
    amount: float
    status: str
    contribution_type: Optional[str]
    created_at: str


# ============ 辅助函数 ============

def get_or_create_default_actor(db: Session) -> Actor:
    """获取或创建默认Actor（用于演示）"""
    actor = db.query(Actor).filter(Actor.display_name == "Alpha-7").first()
    if not actor:
        actor = Actor(
            display_name="Alpha-7",
            actor_type=ActorType.HUMAN,
            capabilities={"开发": 0.9, "产品": 0.8},
            trust_score=0.9
        )
        db.add(actor)
        db.commit()
        db.refresh(actor)
    return actor


# ============ API 端点 ============

@router.post("/contribute", summary="提交贡献")
async def submit_contribution(
    request: ContributeRequest,
    db: Session = Depends(get_db)
):
    """
    提交贡献
    
    流程：
    1. 创建事件
    2. AI评估价值
    3. 返回评估结果
    """
    # 获取或创建默认Actor
    actor = get_or_create_default_actor(db)
    
    # 创建事件
    event = Event(
        actor_id=actor.id,
        action="contribute",
        content=request.content,
        contribution_type=request.contribution_type or "general",
        contribution_status=ContributionStatus.PENDING,
        ai_analysis=request.details
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # AI评估价值
    evaluator = ContributionEvaluator()
    evaluation = await evaluator.evaluate(event)
    
    # 更新事件
    event.contribution_type = evaluation["contribution_type"]
    event.contribution_value = evaluation["value"]
    event.value_confidence = evaluation["confidence"]
    event.value_calculation = evaluation["calculation_basis"]
    event.ai_analysis = {**event.ai_analysis, "entities": evaluation.get("entities", {})}
    
    db.commit()
    
    return {
        "success": True,
        "event_id": str(event.id),
        "contribution_type": event.contribution_type,
        "estimated_value": float(event.contribution_value) if event.contribution_value else 0,
        "confidence": float(event.value_confidence) if event.value_confidence else 0,
        "message": "贡献已提交，AI正在评估价值",
        "calculation": evaluation["calculation_basis"]
    }


@router.get("/my/contributions", summary="获取我的贡献")
async def get_my_contributions(
    period: str = "this_month",
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    获取我的贡献列表
    
    period: this_month / last_month / this_year / all
    status: pending / verified / rejected
    """
    actor = get_or_create_default_actor(db)
    
    # 时间范围
    now = datetime.utcnow()
    if period == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "last_month":
        start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    elif period == "this_year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = None
    
    # 查询
    query = db.query(Event).filter(Event.actor_id == actor.id)
    
    if start_date:
        query = query.filter(Event.created_at >= start_date)
    
    if status:
        query = query.filter(Event.contribution_status == status)
    
    events = query.order_by(Event.created_at.desc()).limit(limit).all()
    
    # 统计
    total_value = sum(float(e.contribution_value or 0) for e in events if e.contribution_status == ContributionStatus.VERIFIED)
    
    # 按类型分组
    by_type = {}
    for e in events:
        if e.contribution_type:
            if e.contribution_type not in by_type:
                by_type[e.contribution_type] = 0
            by_type[e.contribution_type] += float(e.contribution_value or 0)
    
    return {
        "total_value": total_value,
        "count": len(events),
        "by_type": by_type,
        "contributions": [e.to_dict() for e in events]
    }


@router.post("/contributions/{event_id}/verify", summary="验证贡献")
async def verify_contribution(
    event_id: UUID,
    request: VerifyContributionRequest,
    db: Session = Depends(get_db)
):
    """
    验证贡献
    
    设置实际价值并发放回报
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="贡献不存在")
    
    if event.contribution_status == ContributionStatus.VERIFIED:
        raise HTTPException(status_code=400, detail="贡献已验证")
    
    # 更新事件
    event.actual_value = request.actual_value
    event.contribution_status = ContributionStatus.VERIFIED
    event.verified_at = datetime.utcnow()
    
    # 获取Actor
    actor = db.query(Actor).filter(Actor.id == event.actor_id).first()
    
    # 发放回报
    if actor:
        calculator = RewardCalculator(db)
        result = await calculator.process_event_reward(event, actor)
    else:
        result = {"success": False, "message": "Actor不存在"}
    
    db.commit()
    
    return {
        "success": True,
        "event_id": str(event.id),
        "estimated_value": float(event.contribution_value) if event.contribution_value else 0,
        "actual_value": float(event.actual_value),
        "status": ContributionStatus.VERIFIED,
        "reward_result": result
    }


@router.get("/my/rewards", summary="获取我的回报")
async def get_my_rewards(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取我的回报列表"""
    actor = get_or_create_default_actor(db)
    
    calculator = RewardCalculator(db)
    rewards = calculator.get_actor_rewards(actor.id, status)
    available = calculator.get_available_rewards(actor.id)
    
    return {
        "total_rewards": float(actor.total_rewards) if actor.total_rewards else 0,
        "available_rewards": float(actor.available_rewards) if actor.available_rewards else 0,
        "pending_rewards": available,
        "rewards": rewards
    }


@router.post("/rewards/{reward_id}/claim", summary="兑现回报")
async def claim_reward(
    reward_id: UUID,
    request: ClaimRewardRequest,
    db: Session = Depends(get_db)
):
    """兑现回报"""
    actor = get_or_create_default_actor(db)
    
    calculator = RewardCalculator(db)
    result = await calculator.claim_reward(reward_id, actor.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/contributions/leaderboard", summary="贡献排行榜")
async def get_contributions_leaderboard(
    period: str = "this_month",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取贡献排行榜"""
    # 时间范围
    now = datetime.utcnow()
    if period == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = now.replace(month=1, day=1)
    
    # 查询所有Actor的贡献
    actors = db.query(Actor).all()
    
    leaderboard = []
    for actor in actors:
        events = db.query(Event).filter(
            Event.actor_id == actor.id,
            Event.contribution_status == ContributionStatus.VERIFIED,
            Event.created_at >= start_date
        ).all()
        
        total = sum(float(e.actual_value or 0) for e in events)
        if total > 0:
            leaderboard.append({
                "actor_id": str(actor.id),
                "display_name": actor.display_name,
                "total_contributions": total,
                "contribution_count": len(events)
            })
    
    # 排序
    leaderboard.sort(key=lambda x: x["total_contributions"], reverse=True)
    
    return {
        "period": period,
        "leaderboard": leaderboard[:limit]
    }
