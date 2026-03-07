"""
AI Core - 智能中枢

AI Core是系统的大脑，负责：
1. 理解用户意图
2. 提取实体信息
3. 生成任务
4. 智能分配
5. 权限判断
"""

from app.ai.intent_engine import IntentEngine, Intent, IntentResult, get_intent_engine
from app.ai.task_generator import TaskGenerator, GeneratedTask, get_task_generator
from app.ai.smart_assigner import SmartAssigner, AssignmentScore


class AICore:
    """AI核心引擎"""
    
    def __init__(self, db=None):
        self.db = db
        self.intent_engine = get_intent_engine()
        self.task_generator = get_task_generator()
        self.smart_assigner = SmartAssigner(db) if db else None
    
    async def process_input(
        self, 
        actor_id: str, 
        content: str, 
        attachments: list = None,
        actor_info: dict = None
    ):
        """
        处理用户输入
        
        Args:
            actor_id: 参与者ID
            content: 输入内容
            attachments: 附件列表
            actor_info: Actor 信息
            
        Returns:
            处理结果，包括理解、生成的任务等
        """
        # 1. 理解意图
        intent_result = await self.intent_engine.understand(content)
        
        # 2. 获取 Actor 信息
        if not actor_info and self.db:
            from app.services.actor_service import ActorService
            from uuid import UUID
            actor_service = ActorService(self.db)
            actor = actor_service.get_actor(UUID(actor_id))
            if actor:
                actor_info = actor.to_dict()
        
        actor_info = actor_info or {}
        
        # 3. 生成任务
        tasks = await self.task_generator.generate_tasks(
            intent_result=intent_result,
            content=content,
            actor_info=actor_info
        )
        
        # 4. 智能分配
        assigned_tasks = []
        if self.smart_assigner and tasks:
            for task in tasks:
                assignee = self.smart_assigner.find_best_assignee(
                    required_capabilities=task.required_capabilities
                )
                if assignee:
                    task.metadata = task.metadata or {}
                    task.metadata["assigned_to"] = str(assignee.actor_id)
                    task.metadata["assignment_score"] = assignee.score
                    task.metadata["assignment_reasons"] = assignee.reasons
                assigned_tasks.append(task)
        
        # 5. 确定贡献类型和价值
        contribution_type = None
        estimated_value = 0
        
        if intent_result.intent.value == "contribute":
            contribution_type = self.intent_engine.get_contribution_type(
                content, intent_result
            )
            # 从实体中提取金额作为预估价值
            for entity in intent_result.entities:
                if entity.type.value == "amount":
                    estimated_value = entity.value
                    break
        
        return {
            "actor_id": actor_id,
            "understood": {
                "intent": intent_result.intent.value,
                "sub_intent": intent_result.sub_intent,
                "entities": [e.to_dict() for e in intent_result.entities],
                "confidence": intent_result.confidence,
                "reasoning": intent_result.reasoning
            },
            "contribution": {
                "type": contribution_type,
                "estimated_value": estimated_value
            },
            "tasks_created": [t.to_dict() for t in assigned_tasks],
            "message": self._generate_response(intent_result, assigned_tasks)
        }
    
    async def answer_query(self, question: str, context: dict = None):
        """
        回答查询
        
        Args:
            question: 问题
            context: 上下文
            
        Returns:
            回答
        """
        # 1. 理解问题意图
        intent_result = await self.intent_engine.understand(question)
        
        # 2. 搜索相关数据（待实现向量搜索）
        # relevant_events = await self._search_events(question)
        
        # 3. 使用 AI 生成回答
        answer = await self._generate_answer(question, context)
        
        return {
            "question": question,
            "intent": intent_result.intent.value,
            "answer": answer,
            "confidence": intent_result.confidence
        }
    
    def _generate_response(self, intent_result: IntentResult, tasks: list) -> str:
        """生成响应消息"""
        intent = intent_result.intent
        
        if intent == Intent.CONTRIBUTE:
            if tasks:
                return f"我理解您的贡献。已创建 {len(tasks)} 个任务需要处理。"
            return "我理解您的贡献，系统已自动记录。"
        
        elif intent == Intent.QUERY:
            return "让我为您查询相关信息..."
        
        elif intent == Intent.QUESTION:
            return "我已收到您的问题，正在思考..."
        
        elif intent == Intent.APPROVE:
            return "已记录您的审批意见。"
        
        elif intent == Intent.COMMAND:
            return "正在执行您的命令..."
        
        return "我已理解您的输入。"
    
    async def _generate_answer(self, question: str, context: dict = None):
        """使用 AI 生成回答"""
        if not self.intent_engine.client:
            return "AI 服务未配置，无法回答问题。"
        
        try:
            response = self.intent_engine.client.chat.completions.create(
                model=self.intent_engine.model,
                messages=[
                    {"role": "system", "content": "你是 Mozart AI ERP 的智能助手，帮助企业员工查询信息、解答问题。"},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"回答生成失败：{str(e)}"


# 全局AI Core实例
_ai_core = None


def get_ai_core(db=None) -> AICore:
    """获取 AI Core 实例"""
    global _ai_core
    if _ai_core is None or db:
        _ai_core = AICore(db)
    return _ai_core
