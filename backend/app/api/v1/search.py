"""
语义搜索 API

路由：
- POST /search - 语义搜索
- GET  /search/similar/{event_id} - 相似事件
- POST /search/actors - 搜索 Actor
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.vector_service import get_vector_store


router = APIRouter(prefix="/search", tags=["语义搜索"])


# ========== Schemas ==========

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="搜索查询")
    top_k: int = Field(default=10, ge=1, le=50, description="返回数量")
    filters: Optional[Dict] = Field(default=None, description="过滤条件")


class SearchResult(BaseModel):
    """搜索结果"""
    id: str
    content: str
    similarity: float
    contribution_type: Optional[str] = None
    contribution_value: Optional[float] = None
    created_at: Optional[str] = None


# ========== Routes ==========

@router.post("", summary="语义搜索")
async def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    语义搜索事件

    使用向量相似度搜索相关事件

    示例：
    POST /api/v1/search
    {
        "query": "土豆采购",
        "top_k": 10,
        "filters": {"contribution_type": "purchase"}
    }
    """
    vector_store = get_vector_store(db)

    results = await vector_store.search(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters
    )

    return {
        "query": request.query,
        "total": len(results),
        "results": results
    }


@router.get("/similar/{event_id}", summary="相似事件")
async def find_similar_events(
    event_id: str,
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    查找与指定事件相似的事件

    基于向量相似度查找
    """
    vector_store = get_vector_store(db)

    results = await vector_store.search_similar_events(
        event_id=event_id,
        top_k=top_k
    )

    return {
        "event_id": event_id,
        "similar_events": results
    }


@router.get("/suggest", summary="搜索建议")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    获取搜索建议

    基于历史事件提供搜索建议
    """
    # 简单实现：返回最近的贡献类型
    from app.models.contribution import Event
    from sqlalchemy import func

    # 获取最常见的贡献类型
    types = db.query(
        Event.contribution_type,
        func.count(Event.id).label("count")
    ).filter(
        Event.contribution_type.isnot(None),
        Event.content.ilike(f"%{query}%")
    ).group_by(
        Event.contribution_type
    ).order_by(
        func.count(Event.id).desc()
    ).limit(5).all()

    suggestions = [
        {"type": t[0], "count": t[1]}
        for t in types if t[0]
    ]

    return {
        "query": query,
        "suggestions": suggestions
    }


@router.post("/actors", summary="搜索 Actor")
async def search_actors(
    query: str = Query(..., min_length=1),
    capability: Optional[str] = Query(None, description="能力过滤"),
    min_trust: Optional[float] = Query(None, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    搜索 Actor

    可以按名称、能力、信任分数搜索
    """
    from app.models.contribution import Actor
    from sqlalchemy import or_

    query_obj = db.query(Actor).filter(
        Actor.display_name.ilike(f"%{query}%")
    )

    if min_trust is not None:
        query_obj = query_obj.filter(Actor.trust_score >= min_trust)

    actors = query_obj.limit(limit).all()

    # 如果指定了能力，过滤结果
    if capability:
        actors = [
            a for a in actors
            if a.capabilities and capability in a.capabilities
        ]

    return {
        "query": query,
        "total": len(actors),
        "actors": [a.to_dict() for a in actors]
    }
