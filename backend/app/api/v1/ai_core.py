"""
原生AI API架构

不再是传统的 POST /purchases, GET /sales
而是统一的输入和查询接口，AI负责理解和路由

核心AI中枢架构：
- 所有请求都通过核心AI处理
- 真实员工和虚拟AI员工都是Actor
- 支持互相请求任务、协作、对话
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.services.ai_service import AIService
from app.services.central_ai_service import CentralAIService
from app.services.ocr_service import OCRService
from app.models.contribution import Actor, ActorType

router = APIRouter()


# ==================== Pydantic模型 ====================

class ChatRequest(BaseModel):
    """对话请求"""
    actor_id: str  # 当前Actor ID
    message: str
    attachments: Optional[List[str]] = None


class TaskRequest(BaseModel):
    """任务请求"""
    from_actor_id: str  # 发起者
    to_actor_name: str  # 目标Actor名称
    task_description: str
    priority: Optional[int] = 50


class AIChatRequest(BaseModel):
    """请求AI员工处理任务"""
    from_actor_id: str
    to_ai_agent_name: str
    message: str
    context: Optional[dict] = None


class AICreateRequest(BaseModel):
    """创建AI员工请求"""
    display_name: str  # AI员工名称，如 "AI-小助理"
    role: str  # 角色描述，如 "擅长文案撰写"
    description: str  # 详细描述
    capabilities: List[str]  # 能力列表
    system_prompt: str  # 系统提示词
    model: Optional[str] = "deepseek"
    temperature: Optional[float] = 0.7


@router.post("/input")
async def universal_input(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(),
    ocr_service: OCRService = Depends(),
):
    """
    统一输入接口 - 原生AI的核心

    用户可以：
    - 发送文字："今天采购了20斤土豆35元一斤供应商张三"
    - 上传图片：发票、采购单、收据
    - 语音输入：（未来支持）

    AI会：
    1. 理解用户意图（采购？销售？查询？）
    2. 提取关键信息（商品、数量、价格、日期等）
    3. 存储为业务事件
    4. 返回确认信息

    示例：
    POST /api/v1/input
    {
        "text": "今天采购了20斤土豆35元一斤供应商张三"
    }

    响应：
    {
        "status": "success",
        "event_id": 123,
        "understood": {
            "intent": "purchase",
            "confidence": 0.95,
            "extracted": {
                "item": "土豆",
                "quantity": 20,
                "unit": "斤",
                "unit_price": 35,
                "total_amount": 700,
                "supplier": "张三",
                "date": "2026-03-06"
            }
        },
        "message": "已记录采购：土豆 20斤，共700元"
    }
    """
    # TODO: 实现逻辑
    pass


@router.post("/query")
async def natural_language_query(
    query: str,
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(),
):
    """
    自然语言查询接口

    用户可以问任何问题：
    - "本月采购了多少钱？"
    - "土豆的平均价格是多少？"
    - "上周营业额比这周怎么样？"
    - "张三供应商一共给我们供货多少次？"

    AI会：
    1. 理解查询意图
    2. 从事件流中检索相关数据
    3. 进行计算和分析
    4. 用自然语言回答

    示例：
    POST /api/v1/query
    {
        "query": "本月采购了多少钱？"
    }

    响应：
    {
        "answer": "本月（2026年3月）共采购了15,230元，包括23笔采购记录。",
        "data": {
            "total_amount": 15230,
            "count": 23,
            "period": "2026-03"
        },
        "visualization": {
            "type": "bar_chart",
            "data": [...]
        }
    }
    """
    # TODO: 实现逻辑
    pass


@router.get("/events")
async def get_events(
    intent: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    事件流查询接口（可选）

    这是一个"后门"接口，用于：
    - 开发调试
    - 数据审计
    - 高级用户查看原始事件

    普通用户应该使用 /query 接口
    """
    # TODO: 实现逻辑
    pass


@router.post("/events/{event_id}/approve")
async def approve_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    审批事件

    对于重要的业务事件（如大额采购），可能需要人工审批
    """
    # TODO: 实现逻辑
    pass


# ==================== 核心AI交互API ====================

@router.post("/chat")
async def chat_with_central_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    与核心AI对话 - 统一入口
    
    用户发送任何消息，核心AI自动理解意图并处理：
    - 贡献记录 → 自动评估价值
    - 查询请求 → 返回数据分析
    - 任务请求 → 分发给对应Actor
    - AI对话 → 调用AI员工处理
    
    示例请求：
    {
        "actor_id": "uuid-of-actor",
        "message": "今天采购了20斤土豆35元一斤"
    }
    """
    central_ai = CentralAIService(db)
    
    try:
        result = await central_ai.process_input(
            actor_id=UUID(request.actor_id),
            message=request.message,
            attachments=request.attachments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request-ai")
async def request_ai_agent(
    request: AIChatRequest,
    db: Session = Depends(get_db),
):
    """
    请求虚拟AI员工处理任务
    
    示例请求：
    {
        "from_actor_id": "uuid-of-alpha7",
        "to_ai_agent_name": "AI-小助理",
        "message": "帮我写一个产品介绍"
    }
    """
    central_ai = CentralAIService(db)
    
    try:
        result = await central_ai.request_ai_agent(
            from_actor_id=UUID(request.from_actor_id),
            to_ai_agent_name=request.to_ai_agent_name,
            message=request.message,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request-task")
async def request_task_from_actor(
    request: TaskRequest,
    db: Session = Depends(get_db),
):
    """
    请求另一个Actor处理任务
    
    示例请求：
    {
        "from_actor_id": "uuid-of-alpha7",
        "to_actor_name": "Beta-3",
        "task_description": "帮我审核这份合同",
        "priority": 80
    }
    """
    central_ai = CentralAIService(db)
    
    # 查找目标Actor
    to_actor = db.query(Actor).filter(
        Actor.display_name == request.to_actor_name
    ).first()
    
    if not to_actor:
        raise HTTPException(status_code=404, detail=f"Actor {request.to_actor_name} 不存在")
    
    try:
        result = await central_ai.request_human_task(
            from_actor_id=UUID(request.from_actor_id),
            to_actor_id=to_actor.id,
            task_description=request.task_description,
            priority=request.priority
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{actor_id}")
async def get_interaction_history(
    actor_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    获取Actor的交互历史
    
    返回该Actor所有的对话、任务请求、AI协作等记录
    """
    central_ai = CentralAIService(db)
    
    try:
        history = central_ai.get_interaction_history(
            actor_id=UUID(actor_id),
            limit=limit
        )
        return {"interactions": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Actor管理API ====================

@router.get("/actors")
async def list_actors(
    actor_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    获取所有Actor列表
    
    可按类型筛选：
    - human: 真实员工
    - ai_agent: 虚拟AI员工
    - external: 外部合作者
    """
    query = db.query(Actor)
    
    if actor_type:
        query = query.filter(Actor.actor_type == actor_type)
    
    actors = query.order_by(Actor.created_at.desc()).all()
    
    return {
        "actors": [a.to_dict() for a in actors],
        "total": len(actors)
    }


@router.get("/actors/{actor_id}")
async def get_actor(
    actor_id: str,
    db: Session = Depends(get_db),
):
    """获取单个Actor详情"""
    actor = db.query(Actor).filter(Actor.id == UUID(actor_id)).first()
    
    if not actor:
        raise HTTPException(status_code=404, detail="Actor不存在")
    
    return actor.to_dict(include_ai_config=True)


# ==================== 虚拟AI员工管理API ====================

@router.post("/ai-agents")
async def create_ai_agent(
    request: AICreateRequest,
    db: Session = Depends(get_db),
):
    """
    创建虚拟AI员工
    
    示例请求：
    {
        "display_name": "AI-小助理",
        "role": "AI助手",
        "description": "擅长文案撰写、数据分析",
        "capabilities": ["文案", "分析", "整理"],
        "system_prompt": "你是公司的AI助手，负责帮助员工处理各种任务...",
        "model": "deepseek",
        "temperature": 0.7
    }
    """
    # 检查名称是否已存在
    existing = db.query(Actor).filter(
        Actor.display_name == request.display_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="AI员工名称已存在")
    
    # 创建AI员工
    ai_agent = Actor(
        display_name=request.display_name,
        actor_type=ActorType.AI_AGENT,
        capabilities={cap: 0.8 for cap in request.capabilities},
        ai_config={
            "role": request.role,
            "description": request.description,
            "capabilities": request.capabilities,
            "system_prompt": request.system_prompt,
            "model": request.model,
            "temperature": request.temperature
        }
    )
    
    db.add(ai_agent)
    db.commit()
    db.refresh(ai_agent)
    
    return {
        "success": True,
        "ai_agent": ai_agent.to_dict(include_ai_config=True)
    }


@router.get("/ai-agents")
async def list_ai_agents(
    db: Session = Depends(get_db),
):
    """获取所有虚拟AI员工列表"""
    agents = db.query(Actor).filter(
        Actor.actor_type == ActorType.AI_AGENT
    ).all()
    
    return {
        "ai_agents": [a.to_dict(include_ai_config=True) for a in agents],
        "total": len(agents)
    }


@router.delete("/ai-agents/{agent_id}")
async def delete_ai_agent(
    agent_id: str,
    db: Session = Depends(get_db),
):
    """删除虚拟AI员工"""
    agent = db.query(Actor).filter(
        Actor.id == UUID(agent_id),
        Actor.actor_type == ActorType.AI_AGENT
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="AI员工不存在")
    
    db.delete(agent)
    db.commit()
    
    return {"success": True, "message": f"AI员工 {agent.display_name} 已删除"}
