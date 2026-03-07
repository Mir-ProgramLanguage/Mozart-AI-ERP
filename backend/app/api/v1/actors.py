"""
Actor 管理 API

路由：
- GET  /actors              - 获取 Actor 列表
- POST /actors              - 创建 Actor
- GET  /actors/{id}         - 获取 Actor 详情
- PUT  /actors/{id}         - 更新 Actor
- GET  /actors/{id}/capabilities - 获取能力图谱
- POST /actors/{id}/grow    - 能力成长
- GET  /actors/leaderboard  - 排行榜
- GET  /actors/{id}/stats   - 统计信息
"""
from typing import Optional, List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contribution import Actor, ActorType
from app.services.actor_service import ActorService


router = APIRouter(prefix="/actors", tags=["Actor管理"])


# ========== Schemas ==========

class ActorCreateRequest(BaseModel):
    """创建 Actor 请求"""
    display_name: str = Field(..., min_length=2, max_length=50, description="代号")
    actor_type: str = Field(default="human", description="类型: human/ai_agent/external")
    user_id: Optional[int] = Field(None, description="关联用户ID")
    capabilities: Optional[Dict[str, float]] = Field(default={}, description="初始能力")
    ai_config: Optional[Dict] = Field(default={}, description="AI配置（虚拟员工）")


class ActorUpdateRequest(BaseModel):
    """更新 Actor 请求"""
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    capabilities: Optional[Dict[str, float]] = None
    availability: Optional[float] = Field(None, ge=0, le=1)
    ai_config: Optional[Dict] = None


class CapabilityGrowRequest(BaseModel):
    """能力成长请求"""
    capability_name: str = Field(..., description="能力名称")
    contribution_value: float = Field(..., ge=0, description="贡献价值")
    reason: Optional[str] = Field("", description="成长原因")


class ActorResponse(BaseModel):
    """Actor 响应"""
    id: str
    display_name: str
    actor_type: str
    capabilities: Dict[str, float]
    total_contributions: float
    total_rewards: float
    available_rewards: float
    trust_score: float
    reputation_score: float
    contribution_count: int
    availability: float
    created_at: str
    last_active: str

    class Config:
        from_attributes = True


# ========== Routes ==========

@router.get("", summary="获取 Actor 列表")
async def list_actors(
    actor_type: Optional[str] = Query(None, description="类型过滤"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """获取 Actor 列表"""
    service = ActorService(db)
    actors = service.list_actors(actor_type=actor_type, limit=limit)
    return {
        "total": len(actors),
        "actors": [a.to_dict() for a in actors]
    }


@router.post("", summary="创建 Actor")
async def create_actor(
    request: ActorCreateRequest,
    db: Session = Depends(get_db)
):
    """创建 Actor"""
    service = ActorService(db)

    # 检查名称是否已存在
    existing = service.get_actor_by_name(request.display_name)
    if existing:
        raise HTTPException(status_code=400, detail="代号已存在")

    actor = service.create_actor(
        display_name=request.display_name,
        actor_type=request.actor_type,
        user_id=request.user_id,
        capabilities=request.capabilities,
        ai_config=request.ai_config
    )

    return {
        "message": "Actor 创建成功",
        "actor": actor.to_dict()
    }


@router.get("/leaderboard", summary="排行榜")
async def get_leaderboard(
    by: str = Query("total_contributions", description="排序字段"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取排行榜"""
    service = ActorService(db)
    valid_fields = ["total_contributions", "trust_score", "reputation_score"]
    if by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"无效的排序字段，可选: {valid_fields}")

    leaderboard = service.get_leaderboard(by=by, limit=limit)
    return {
        "by": by,
        "leaderboard": leaderboard
    }


@router.get("/{actor_id}", summary="获取 Actor 详情")
async def get_actor(
    actor_id: UUID,
    db: Session = Depends(get_db)
):
    """获取 Actor 详情"""
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")
    return actor.to_dict()


@router.put("/{actor_id}", summary="更新 Actor")
async def update_actor(
    actor_id: UUID,
    request: ActorUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新 Actor"""
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    # 更新字段
    if request.display_name:
        # 检查新名称是否已存在
        existing = service.get_actor_by_name(request.display_name)
        if existing and str(existing.id) != str(actor_id):
            raise HTTPException(status_code=400, detail="代号已存在")
        actor.display_name = request.display_name

    if request.capabilities is not None:
        actor.capabilities = request.capabilities

    if request.availability is not None:
        actor.availability = request.availability

    if request.ai_config is not None:
        actor.ai_config = request.ai_config

    db.commit()
    db.refresh(actor)

    return {
        "message": "更新成功",
        "actor": actor.to_dict()
    }


@router.get("/{actor_id}/capabilities", summary="获取能力图谱")
async def get_capabilities(
    actor_id: UUID,
    db: Session = Depends(get_db)
):
    """获取 Actor 的能力图谱"""
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    # 获取能力排名
    capabilities = actor.capabilities or {}
    ranked_capabilities = []
    for cap_name, value in capabilities.items():
        rank = service.get_capability_rank(actor, cap_name)
        ranked_capabilities.append({
            "name": cap_name,
            "value": value,
            "rank": rank
        })

    # 按能力值排序
    ranked_capabilities.sort(key=lambda x: x["value"], reverse=True)

    return {
        "display_name": actor.display_name,
        "capabilities": ranked_capabilities,
        "overall_score": sum(capabilities.values()) / len(capabilities) if capabilities else 0
    }


@router.post("/{actor_id}/grow", summary="能力成长")
async def grow_capability(
    actor_id: UUID,
    request: CapabilityGrowRequest,
    db: Session = Depends(get_db)
):
    """
    促进能力成长

    成长公式：delta = 0.01 * (1 + value/10000) * (1 - current)
    """
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    new_value = service.grow_capability(
        actor=actor,
        capability_name=request.capability_name,
        contribution_value=request.contribution_value,
        reason=request.reason or ""
    )

    return {
        "message": "能力成长成功",
        "capability_name": request.capability_name,
        "new_value": new_value,
        "growth": new_value - (actor.capabilities.get(request.capability_name, 0) - (new_value - actor.capabilities.get(request.capability_name, 0)))
    }


@router.get("/{actor_id}/stats", summary="统计信息")
async def get_stats(
    actor_id: UUID,
    db: Session = Depends(get_db)
):
    """获取 Actor 统计信息"""
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    # 更新统计
    service.update_statistics(actor)

    return {
        "display_name": actor.display_name,
        "total_contributions": float(actor.total_contributions or 0),
        "total_rewards": float(actor.total_rewards or 0),
        "available_rewards": float(actor.available_rewards or 0),
        "contribution_count": actor.contribution_count or 0,
        "contributions_by_type": actor.contributions_by_type or {},
        "trust_score": float(actor.trust_score or 0.5),
        "reputation_score": float(actor.reputation_score or 0.5),
        "capability_count": len(actor.capabilities) if actor.capabilities else 0,
        "capability_history_count": len(actor.capability_history) if actor.capability_history else 0
    }


@router.post("/{actor_id}/trust", summary="更新信任分数")
async def update_trust(
    actor_id: UUID,
    success: bool = Query(..., description="是否成功"),
    magnitude: float = Query(1.0, ge=0.1, le=5.0, description="影响系数"),
    db: Session = Depends(get_db)
):
    """更新信任分数"""
    service = ActorService(db)
    actor = service.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    new_score = service.update_trust_score(actor, success, magnitude)

    return {
        "message": "信任分数已更新",
        "success": success,
        "new_trust_score": new_score
    }
