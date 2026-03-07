"""
Task 管理 API

路由：
- GET  /tasks              - 获取任务列表
- POST /tasks              - 创建任务
- GET  /tasks/{id}         - 获取任务详情
- PUT  /tasks/{id}         - 更新任务
- POST /tasks/{id}/assign  - 分配任务
- POST /tasks/{id}/start   - 开始任务
- POST /tasks/{id}/complete - 完成任务
- POST /tasks/{id}/verify  - 验证任务
- GET  /tasks/available    - 可领取的任务
- GET  /tasks/my           - 我的任务
"""
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contribution import Actor, Task, Event
from app.services.actor_service import ActorService


router = APIRouter(prefix="/tasks", tags=["任务管理"])


# ========== Schemas ==========

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    type: str = Field(..., description="任务类型: verify/approve/execute/evaluate/review/deliver")
    description: str = Field(..., min_length=5, description="任务描述")
    priority: int = Field(default=50, ge=0, le=100, description="优先级 0-100")
    related_events: Optional[List[str]] = Field(default=[], description="关联事件ID")
    required_capabilities: Optional[Dict[str, float]] = Field(default={}, description="所需能力")
    deadline: Optional[datetime] = Field(None, description="截止时间")


class TaskAssignRequest(BaseModel):
    """分配任务请求"""
    actor_id: str = Field(..., description="分配给 Actor ID")


class TaskCompleteRequest(BaseModel):
    """完成任务请求"""
    result: str = Field(..., description="任务结果")
    result_value: Optional[float] = Field(None, ge=0, description="实际价值")


class TaskVerifyRequest(BaseModel):
    """验证任务请求"""
    approved: bool = Field(..., description="是否通过")
    notes: Optional[str] = Field("", description="验证备注")


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    type: str
    description: str
    priority: int
    status: str
    assigned_to: List[str]
    created_at: str

    class Config:
        from_attributes = True


# ========== Routes ==========

@router.get("", summary="获取任务列表")
async def list_tasks(
    status: Optional[str] = Query(None, description="状态过滤"),
    task_type: Optional[str] = Query(None, description="类型过滤"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.type == task_type)

    tasks = query.order_by(Task.priority.desc(), Task.created_at.desc()).limit(limit).all()

    return {
        "total": len(tasks),
        "tasks": [t.to_dict() for t in tasks]
    }


@router.post("", summary="创建任务")
async def create_task(
    request: TaskCreateRequest,
    db: Session = Depends(get_db)
):
    """创建任务"""
    task = Task(
        type=request.type,
        description=request.description,
        priority=request.priority,
        related_events=[UUID(e) for e in request.related_events] if request.related_events else [],
        deadline=request.deadline,
        status="pending"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "任务创建成功",
        "task": task.to_dict()
    }


@router.get("/available", summary="可领取的任务")
async def get_available_tasks(
    actor_id: Optional[str] = Query(None, description="当前 Actor ID"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取可领取的任务"""
    query = db.query(Task).filter(
        Task.status == "pending",
        (Task.assigned_to == None) | (Task.assigned_to == [])
    )

    tasks = query.order_by(Task.priority.desc()).limit(limit).all()

    # 如果提供了 actor_id，计算匹配度
    result = []
    if actor_id:
        actor_service = ActorService(db)
        actor = actor_service.get_actor(UUID(actor_id))
        if actor:
            for task in tasks:
                task_dict = task.to_dict()
                # 计算匹配分数
                # 这里可以扩展为更复杂的匹配逻辑
                task_dict["match_score"] = 0.5  # 默认
                result.append(task_dict)
        else:
            result = [t.to_dict() for t in tasks]
    else:
        result = [t.to_dict() for t in tasks]

    return {
        "total": len(result),
        "tasks": result
    }


@router.get("/my", summary="我的任务")
async def get_my_tasks(
    actor_id: str = Query(..., description="Actor ID"),
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db)
):
    """获取分配给我的任务"""
    query = db.query(Task).filter(
        Task.assigned_to.contains([UUID(actor_id)])
    )

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.priority.desc(), Task.created_at.desc()).all()

    return {
        "total": len(tasks),
        "tasks": [t.to_dict() for t in tasks]
    }


@router.get("/{task_id}", summary="获取任务详情")
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task.to_dict()


@router.put("/{task_id}", summary="更新任务")
async def update_task(
    task_id: UUID,
    description: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    deadline: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if description:
        task.description = description
    if priority is not None:
        task.priority = priority
    if deadline:
        task.deadline = deadline

    db.commit()
    db.refresh(task)

    return {
        "message": "更新成功",
        "task": task.to_dict()
    }


@router.post("/{task_id}/assign", summary="分配任务")
async def assign_task(
    task_id: UUID,
    request: TaskAssignRequest,
    db: Session = Depends(get_db)
):
    """分配任务给 Actor"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    actor_service = ActorService(db)
    actor = actor_service.get_actor(UUID(request.actor_id))
    if not actor:
        raise HTTPException(status_code=404, detail="Actor 不存在")

    # 分配任务
    if not task.assigned_to:
        task.assigned_to = []
    task.assigned_to = task.assigned_to + [UUID(request.actor_id)]
    task.status = "assigned"

    db.commit()
    db.refresh(task)

    return {
        "message": f"任务已分配给 {actor.display_name}",
        "task": task.to_dict()
    }


@router.post("/{task_id}/auto-assign", summary="自动分配任务")
async def auto_assign_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    """AI 自动分配任务给最合适的 Actor"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # TODO: 根据任务类型推断所需能力
    required_capabilities = {}  # 可以从任务类型推断

    actor_service = ActorService(db)
    best_actor = actor_service.find_best_match(required_capabilities)

    if not best_actor:
        raise HTTPException(status_code=404, detail="没有找到合适的 Actor")

    # 分配任务
    task.assigned_to = [best_actor.id]
    task.status = "assigned"

    db.commit()
    db.refresh(task)

    return {
        "message": f"任务已自动分配给 {best_actor.display_name}",
        "actor": best_actor.to_dict(),
        "task": task.to_dict()
    }


@router.post("/{task_id}/start", summary="开始任务")
async def start_task(
    task_id: UUID,
    actor_id: str = Query(..., description="Actor ID"),
    db: Session = Depends(get_db)
):
    """开始执行任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "assigned":
        raise HTTPException(status_code=400, detail="任务状态不允许开始")

    task.status = "in_progress"
    task.started_at = datetime.utcnow()  # Note: 需要在模型中添加此字段

    db.commit()
    db.refresh(task)

    return {
        "message": "任务已开始",
        "task": task.to_dict()
    }


@router.post("/{task_id}/complete", summary="完成任务")
async def complete_task(
    task_id: UUID,
    request: TaskCompleteRequest,
    db: Session = Depends(get_db)
):
    """完成任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "in_progress":
        raise HTTPException(status_code=400, detail="任务状态不允许完成")

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    # TODO: 触发贡献评估和回报计算

    return {
        "message": "任务已完成",
        "task": task.to_dict()
    }


@router.post("/{task_id}/verify", summary="验证任务")
async def verify_task(
    task_id: UUID,
    request: TaskVerifyRequest,
    verifier_id: str = Query(..., description="验证者 Actor ID"),
    db: Session = Depends(get_db)
):
    """验证已完成的任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="只有已完成的任务可以验证")

    # 更新验证信息
    # Note: 需要在模型中添加验证相关字段

    if not request.approved:
        task.status = "pending"  # 需要重新处理

    db.commit()
    db.refresh(task)

    return {
        "message": "验证通过" if request.approved else "验证未通过，需重新处理",
        "approved": request.approved,
        "task": task.to_dict()
    }


@router.post("/{task_id}/cancel", summary="取消任务")
async def cancel_task(
    task_id: UUID,
    reason: str = Query("", description="取消原因"),
    db: Session = Depends(get_db)
):
    """取消任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="任务状态不允许取消")

    task.status = "cancelled"

    db.commit()
    db.refresh(task)

    return {
        "message": "任务已取消",
        "reason": reason,
        "task": task.to_dict()
    }
