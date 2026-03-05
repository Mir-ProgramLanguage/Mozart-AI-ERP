"""
AI Core - 智能中枢

AI Core是系统的大脑，负责：
1. 理解用户意图
2. 提取实体信息
3. 生成任务
4. 智能分配
5. 权限判断
"""

from app.ai.intent_engine import IntentEngine
from app.ai.entity_engine import EntityEngine
from app.ai.task_engine import TaskEngine
from app.ai.assignment_engine import AssignmentEngine
from app.ai.permission_engine import PermissionEngine


class AICore:
    """AI核心引擎"""
    
    def __init__(self):
        self.intent_engine = IntentEngine()
        self.entity_engine = EntityEngine()
        self.task_engine = TaskEngine()
        self.assignment_engine = AssignmentEngine()
        self.permission_engine = PermissionEngine()
    
    async def process_input(self, actor_id: str, content: str, attachments: list = None):
        """
        处理用户输入
        
        Args:
            actor_id: 参与者ID
            content: 输入内容
            attachments: 附件列表
            
        Returns:
            处理结果，包括理解、生成的任务等
        """
        # 1. 理解意图
        intent_result = await self.intent_engine.understand(content)
        
        # 2. 提取实体
        entities = await self.entity_engine.extract(content, intent_result["intent"])
        
        # 3. 判断风险
        risk_level = self._assess_risk(intent_result, entities)
        
        # 4. 生成事件
        event = await self._create_event(
            actor_id=actor_id,
            content=content,
            intent=intent_result,
            entities=entities,
            risk_level=risk_level,
            attachments=attachments
        )
        
        # 5. 生成任务
        tasks = await self.task_engine.generate(event)
        
        # 6. 分配任务
        for task in tasks:
            await self.assignment_engine.assign(task)
        
        return {
            "event_id": event.id,
            "understood": {
                "intent": intent_result["intent"],
                "entities": entities,
                "confidence": intent_result["confidence"]
            },
            "tasks_created": [t.to_dict() for t in tasks],
            "message": self._generate_response(intent_result, tasks)
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
        query_intent = await self.intent_engine.understand_query(question)
        
        # 2. 搜索相关事件
        relevant_events = await self._search_events(question)
        
        # 3. 生成回答
        answer = await self.intent_engine.generate_answer(
            question=question,
            events=relevant_events,
            context=context
        )
        
        return {
            "answer": answer["text"],
            "data": answer.get("data"),
            "sources": [e.id for e in relevant_events[:5]]
        }
    
    def _assess_risk(self, intent_result: dict, entities: dict) -> str:
        """评估风险等级"""
        # 金额风险
        if entities.get("amount"):
            if entities["amount"] > 10000:
                return "high"
            elif entities["amount"] > 5000:
                return "medium"
        
        # 置信度风险
        if intent_result["confidence"] < 0.7:
            return "medium"
        
        return "low"
    
    def _generate_response(self, intent_result: dict, tasks: list) -> str:
        """生成响应消息"""
        intent = intent_result["intent"]
        
        if intent == "record":
            if tasks:
                return f"我理解您记录了一笔业务。已创建{len(tasks)}个任务需要处理。"
            return "我理解您记录了一笔业务。系统已自动记录。"
        
        elif intent == "query":
            return "让我为您查询相关信息..."
        
        elif intent == "question":
            return "我已收到您的问题，正在思考..."
        
        return "我已理解您的输入。"
    
    async def _create_event(self, **kwargs):
        """创建事件（待实现）"""
        # TODO: 实现事件创建逻辑
        pass
    
    async def _search_events(self, query: str):
        """搜索事件（待实现）"""
        # TODO: 实现事件搜索逻辑
        pass


# 全局AI Core实例
ai_core = AICore()
