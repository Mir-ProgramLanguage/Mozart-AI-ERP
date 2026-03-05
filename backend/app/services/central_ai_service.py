"""
核心AI服务 (Central AI Service)

这是整个系统的中枢，负责：
1. 所有请求的意图理解
2. 任务生成和分发
3. Actor之间的交互协调
4. 权限控制和数据访问
5. 交互日志记录

所有真实员工和虚拟AI员工都通过这个服务与系统交互
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from openai import OpenAI

from app.config import settings
from app.models.contribution import (
    Actor, ActorType, Event, Task, ActorInteraction,
    InteractionType, InteractionStatus, ContributionStatus
)


class CentralAIService:
    """
    核心AI服务 - 系统的中枢大脑
    
    所有交互都通过这个服务：
    - 真实员工 → 核心AI → 数据
    - 真实员工 → 核心AI → 请求AI员工处理任务
    - AI员工 → 核心AI → 数据/任务
    - 真实员工 ↔ 真实员工（通过核心AI协调）
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL
    
    # ==================== 核心交互方法 ====================
    
    async def process_input(
        self,
        actor_id: UUID,
        message: str,
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户输入 - 统一入口
        
        步骤：
        1. 识别意图（贡献记录？查询？任务请求？AI对话？）
        2. 根据意图分发处理
        3. 记录交互日志
        """
        # 获取Actor信息
        actor = self.db.query(Actor).filter(Actor.id == actor_id).first()
        if not actor:
            return {"error": "Actor不存在"}
        
        # 理解意图
        intent = await self._understand_intent(message)
        
        # 根据意图分发
        if intent["type"] == "contribution":
            return await self._handle_contribution(actor, message, intent)
        elif intent["type"] == "query":
            return await self._handle_query(actor, message, intent)
        elif intent["type"] == "task_request":
            return await self._handle_task_request(actor, message, intent)
        elif intent["type"] == "ai_chat":
            return await self._handle_ai_chat(actor, message, intent)
        else:
            return await self._handle_general(actor, message, intent)
    
    async def request_ai_agent(
        self,
        from_actor_id: UUID,
        to_ai_agent_name: str,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        请求虚拟AI员工处理任务
        
        示例：
        - "请AI助手帮我写一个产品介绍"
        - "让AI财务专家帮我分析这笔支出"
        """
        # 获取发起者
        from_actor = self.db.query(Actor).filter(Actor.id == from_actor_id).first()
        if not from_actor:
            return {"error": "Actor不存在"}
        
        # 查找目标AI员工
        to_actor = self.db.query(Actor).filter(
            Actor.display_name == to_ai_agent_name,
            Actor.actor_type == ActorType.AI_AGENT
        ).first()
        
        if not to_actor:
            return {"error": f"AI员工 {to_ai_agent_name} 不存在"}
        
        # 记录交互
        interaction = ActorInteraction(
            interaction_type=InteractionType.TASK_REQUEST,
            from_actor_id=from_actor_id,
            from_actor_name=from_actor.display_name,
            to_actor_id=to_actor.id,
            to_actor_name=to_actor.display_name,
            message=message,
            context=context or {},
            status=InteractionStatus.PENDING
        )
        self.db.add(interaction)
        
        # 调用AI员工处理
        ai_response = await self._call_ai_agent(to_actor, message, context)
        
        # 更新交互结果
        interaction.ai_response = ai_response
        interaction.status = InteractionStatus.COMPLETED
        interaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "interaction_id": str(interaction.id),
            "from_actor": from_actor.display_name,
            "to_actor": to_actor.display_name,
            "message": message,
            "response": ai_response
        }
    
    async def request_human_task(
        self,
        from_actor_id: UUID,
        to_actor_id: UUID,
        task_description: str,
        priority: int = 50
    ) -> Dict[str, Any]:
        """
        请求另一个真实员工处理任务
        
        示例：
        - "请Beta3帮我审核这份合同"
        """
        from_actor = self.db.query(Actor).filter(Actor.id == from_actor_id).first()
        to_actor = self.db.query(Actor).filter(Actor.id == to_actor_id).first()
        
        if not from_actor or not to_actor:
            return {"error": "Actor不存在"}
        
        # 创建任务
        task = Task(
            type="approval",
            description=task_description,
            priority=priority,
            assigned_to=[to_actor_id],
            status="pending"
        )
        self.db.add(task)
        
        # 记录交互
        interaction = ActorInteraction(
            interaction_type=InteractionType.TASK_REQUEST,
            from_actor_id=from_actor_id,
            from_actor_name=from_actor.display_name,
            to_actor_id=to_actor_id,
            to_actor_name=to_actor.display_name,
            message=task_description,
            task_id=task.id,
            status=InteractionStatus.PENDING
        )
        self.db.add(interaction)
        self.db.commit()
        
        return {
            "success": True,
            "task_id": str(task.id),
            "from_actor": from_actor.display_name,
            "to_actor": to_actor.display_name,
            "task_description": task_description
        }
    
    async def ai_agents_collaborate(
        self,
        from_ai_agent_id: UUID,
        to_ai_agent_name: str,
        request: str
    ) -> Dict[str, Any]:
        """
        AI员工之间的协作
        
        示例：
        - AI销售专家 → AI技术专家："需要为XX客户生成技术方案"
        """
        from_actor = self.db.query(Actor).filter(Actor.id == from_ai_agent_id).first()
        to_actor = self.db.query(Actor).filter(
            Actor.display_name == to_ai_agent_name,
            Actor.actor_type == ActorType.AI_AGENT
        ).first()
        
        if not from_actor or not to_actor:
            return {"error": "AI员工不存在"}
        
        # 记录协作
        interaction = ActorInteraction(
            interaction_type=InteractionType.AI_COLLABORATION,
            from_actor_id=from_ai_agent_id,
            from_actor_name=from_actor.display_name,
            to_actor_id=to_actor.id,
            to_actor_name=to_actor.display_name,
            message=request,
            status=InteractionStatus.PENDING
        )
        self.db.add(interaction)
        
        # 调用目标AI
        ai_response = await self._call_ai_agent(to_actor, request, {})
        
        interaction.ai_response = ai_response
        interaction.status = InteractionStatus.COMPLETED
        interaction.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "from_ai": from_actor.display_name,
            "to_ai": to_actor.display_name,
            "request": request,
            "response": ai_response
        }
    
    # ==================== 意图理解 ====================
    
    async def _understand_intent(self, message: str) -> Dict[str, Any]:
        """
        理解用户输入的意图
        
        返回：
        {
            "type": "contribution|query|task_request|ai_chat|general",
            "confidence": 0.95,
            "details": {...}
        }
        """
        prompt = f"""
分析用户输入，判断意图类型。

用户输入：{message}

意图类型：
- contribution: 记录贡献（如"今天采购了XX"、"发现了一个供应商"）
- query: 查询数据（如"本月销售额多少？"）
- task_request: 请求任务（如"请XX帮我处理..."、"让AI助手..."）
- ai_chat: 与AI对话（如"帮我写文案"、"分析这个数据"）
- general: 一般对话

请返回JSON：
{{
    "type": "意图类型",
    "confidence": 0.0-1.0,
    "details": {{}}
}}
"""
        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {"type": "general", "confidence": 0.5, "details": {}}
    
    # ==================== 处理器 ====================
    
    async def _handle_contribution(
        self, actor: Actor, message: str, intent: Dict
    ) -> Dict[str, Any]:
        """处理贡献记录"""
        # 创建事件
        event = Event(
            actor_id=actor.id,
            action="contribute",
            content=message,
            ai_analysis=intent.get("details", {}),
            contribution_type="general",
            contribution_status=ContributionStatus.PENDING
        )
        self.db.add(event)
        self.db.commit()
        
        return {
            "success": True,
            "event_id": str(event.id),
            "message": "已记录您的贡献，等待AI评估价值"
        }
    
    async def _handle_query(
        self, actor: Actor, message: str, intent: Dict
    ) -> Dict[str, Any]:
        """处理查询请求"""
        # TODO: 调用现有的查询逻辑
        return {
            "success": True,
            "message": "查询功能开发中..."
        }
    
    async def _handle_task_request(
        self, actor: Actor, message: str, intent: Dict
    ) -> Dict[str, Any]:
        """处理任务请求"""
        # 解析请求的目标
        target = intent.get("details", {}).get("target")
        
        if target:
            # 请求特定人/AI处理
            if target.startswith("AI-") or target.startswith("AI"):
                return await self.request_ai_agent(actor.id, target, message)
            else:
                # 查找真实员工
                target_actor = self.db.query(Actor).filter(
                    Actor.display_name == target,
                    Actor.actor_type == ActorType.HUMAN
                ).first()
                if target_actor:
                    return await self.request_human_task(
                        actor.id, target_actor.id, message
                    )
        
        return {
            "success": False,
            "message": "无法理解任务请求的目标"
        }
    
    async def _handle_ai_chat(
        self, actor: Actor, message: str, intent: Dict
    ) -> Dict[str, Any]:
        """处理AI对话请求"""
        # 查找默认AI助手
        ai_assistant = self.db.query(Actor).filter(
            Actor.actor_type == ActorType.AI_AGENT,
            Actor.display_name.like("%助手%")
        ).first()
        
        if not ai_assistant:
            return {"error": "系统没有配置AI助手"}
        
        return await self.request_ai_agent(
            actor.id, ai_assistant.display_name, message
        )
    
    async def _handle_general(
        self, actor: Actor, message: str, intent: Dict
    ) -> Dict[str, Any]:
        """处理一般对话"""
        # 记录交互
        interaction = ActorInteraction(
            interaction_type=InteractionType.CHAT,
            from_actor_id=actor.id,
            from_actor_name=actor.display_name,
            to_actor_id=actor.id,  # 自己
            to_actor_name=actor.display_name,
            message=message,
            status=InteractionStatus.COMPLETED
        )
        self.db.add(interaction)
        self.db.commit()
        
        return {
            "success": True,
            "message": "已记录您的消息"
        }
    
    # ==================== AI员工调用 ====================
    
    async def _call_ai_agent(
        self,
        ai_actor: Actor,
        message: str,
        context: Dict[str, Any]
    ) -> str:
        """
        调用虚拟AI员工处理任务
        
        使用AI员工的配置（system_prompt、temperature等）
        """
        if not ai_actor.ai_config:
            return "AI员工配置不完整"
        
        config = ai_actor.ai_config
        system_prompt = config.get("system_prompt", "你是公司的AI助手。")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # 添加上下文
        if context:
            messages.insert(1, {
                "role": "system",
                "content": f"上下文信息：{json.dumps(context, ensure_ascii=False)}"
            })
        
        response = self.llm.chat.completions.create(
            model=config.get("model", self.model),
            messages=messages,
            temperature=config.get("temperature", 0.7)
        )
        
        return response.choices[0].message.content
    
    # ==================== 交互历史 ====================
    
    def get_interaction_history(
        self,
        actor_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取交互历史"""
        interactions = self.db.query(ActorInteraction).filter(
            (ActorInteraction.from_actor_id == actor_id) |
            (ActorInteraction.to_actor_id == actor_id)
        ).order_by(ActorInteraction.created_at.desc()).limit(limit).all()
        
        return [i.to_dict() for i in interactions]
