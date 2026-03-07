"""
统一输入/查询接口

核心 API：
- POST /say - 统一输入（用户发言）
- POST /ask - 自然语言查询
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.ai import get_ai_core
from app.services.actor_service import ActorService
from app.services.vector_service import get_vector_store


router = APIRouter(tags=["统一接口"])


# ========== Schemas ==========

class SayRequest(BaseModel):
    """统一输入请求"""
    actor_id: str = Field(..., description="Actor ID")
    message: str = Field(..., min_length=1, max_length=2000, description="消息内容")
    attachments: Optional[List[str]] = Field(default=None, description="附件URL列表")


class SayResponse(BaseModel):
    """统一输入响应"""
    status: str
    event_id: Optional[str] = None
    understood: Dict
    contribution: Optional[Dict] = None
    tasks_created: List[Dict] = []
    message: str


class AskRequest(BaseModel):
    """自然语言查询请求"""
    actor_id: str = Field(..., description="Actor ID")
    question: str = Field(..., min_length=1, max_length=500, description="问题")
    context: Optional[Dict] = Field(default=None, description="上下文")


class AskResponse(BaseModel):
    """自然语言查询响应"""
    question: str
    answer: str
    data: Optional[Dict] = None
    sources: List[Dict] = []


# ========== Routes ==========

@router.post("/say", response_model=SayResponse, summary="统一输入")
async def unified_say(
    request: SayRequest,
    db: Session = Depends(get_db)
):
    """
    统一输入接口 - 用户发言

    这是系统的核心入口。用户发送任何内容，AI会：
    1. 理解意图（贡献/查询/审批/问题）
    2. 提取实体（金额、人员、物品等）
    3. 评估价值（如果是贡献）
    4. 生成任务（如果需要审核）
    5. 存储事件并返回响应
    """
    # 获取或创建 Actor
    actor_service = ActorService(db)
    actor_info = {}
    
    try:
        actor = actor_service.get_actor(UUID(request.actor_id))
        if actor:
            actor_info = actor.to_dict()
    except (ValueError, Exception) as e:
        # Actor 不存在，使用默认信息
        print(f"Actor not found, using default: {e}")
        actor_info = {
            "id": request.actor_id,
            "display_name": "User",
            "trust_score": 0.5,
            "capabilities": {}
        }

    # 调用 AI Core 处理
    ai_core = get_ai_core(db)
    result = await ai_core.process_input(
        actor_id=request.actor_id,
        content=request.message,
        attachments=request.attachments,
        actor_info=actor_info
    )

    # 存储事件到数据库
    event_id = await _store_event(
        db=db,
        actor_id=request.actor_id,
        content=request.message,
        intent=result["understood"]["intent"],
        entities=result["understood"]["entities"],
        contribution=result.get("contribution")
    )

    return SayResponse(
        status="success",
        event_id=event_id,
        understood=result["understood"],
        contribution=result.get("contribution"),
        tasks_created=result["tasks_created"],
        message=result["message"]
    )


@router.post("/ask", response_model=AskResponse, summary="自然语言查询")
async def natural_language_ask(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    """
    自然语言查询接口

    用户可以问任何问题，AI会：
    1. 理解问题意图
    2. 从事件流中搜索相关数据
    3. 生成自然语言回答
    """
    # 语义搜索相关事件（可选，可能没有向量数据库）
    relevant_events = []
    try:
        vector_store = get_vector_store(db)
        relevant_events = await vector_store.search(
            query=request.question,
            top_k=5
        )
    except Exception as e:
        print(f"Vector search error (ignored): {e}")

    # 调用 AI 生成回答
    ai_core = get_ai_core(db)
    result = await ai_core.answer_query(
        question=request.question,
        context={
            **(request.context or {}),
            "relevant_events": relevant_events
        }
    )

    return AskResponse(
        question=request.question,
        answer=result["answer"],
        data={"relevant_events": relevant_events},
        sources=relevant_events[:3]
    )


@router.get("/my/summary", summary="我的概览")
async def get_my_summary(
    actor_id: str = Query(..., description="Actor ID"),
    db: Session = Depends(get_db)
):
    """
    获取 Actor 的概览信息

    包括贡献统计、任务统计、能力图谱等
    """
    actor_service = ActorService(db)

    try:
        actor = actor_service.get_actor(UUID(actor_id))
        if not actor:
            raise HTTPException(status_code=404, detail="Actor 不存在")
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 Actor ID")

    # 更新统计
    actor_service.update_statistics(actor)

    # 获取能力排名
    capability_ranks = []
    for cap_name, value in (actor.capabilities or {}).items():
        rank = actor_service.get_capability_rank(actor, cap_name)
        capability_ranks.append({
            "name": cap_name,
            "value": value,
            "rank": rank
        })

    return {
        "actor": actor.to_dict(),
        "capabilities_ranked": sorted(capability_ranks, key=lambda x: x["value"], reverse=True),
        "overall_score": actor_service.calculate_reputation(actor)
    }


# ========== Helper Functions ==========

async def _store_event(
    db: Session,
    actor_id: str,
    content: str,
    intent: str,
    entities: List[Dict],
    contribution: Optional[Dict]
) -> Optional[str]:
    """存储事件到数据库"""
    from app.models.contribution import Event
    from uuid import uuid4

    try:
        event = Event(
            id=uuid4(),
            actor_id=UUID(actor_id),
            action=intent,
            content=content,
            contribution_type=contribution.get("type") if contribution else None,
            contribution_value=contribution.get("estimated_value") if contribution else None,
            contribution_status="pending",
            ai_analysis={
                "entities": entities,
                "intent": intent
            }
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # 异步向量化（可选）
        # vector_store = get_vector_store(db)
        # await vector_store.store_event(str(event.id), content)

        return str(event.id)
    except Exception as e:
        print(f"Store event error: {e}")
        db.rollback()
        return None
