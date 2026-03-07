"""
任务生成系统 - Task Generator

核心功能：
1. 根据事件自动生成任务
2. 任务优先级算法
3. 任务超时重分配
4. 任务模板管理
"""
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum
import json
import os

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from app.ai.intent_engine import IntentResult, Intent


class TaskTrigger(str, Enum):
    """任务触发条件"""
    HIGH_VALUE = "high_value"           # 高价值贡献
    LOW_TRUST = "low_trust"             # 低信任用户
    FIRST_TIME = "first_time"           # 首次操作
    SUSPICIOUS = "suspicious"           # 可疑操作
    MANUAL_REQUEST = "manual_request"   # 手动请求
    TIMEOUT = "timeout"                 # 超时


@dataclass
class GeneratedTask:
    """生成的任务"""
    type: str
    description: str
    priority: int  # 0-100
    required_capabilities: Dict[str, float]
    deadline: datetime
    trigger: TaskTrigger
    estimated_value: float = 0.0
    metadata: Dict = None

    def to_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "priority": self.priority,
            "required_capabilities": self.required_capabilities,
            "deadline": self.deadline.isoformat(),
            "trigger": self.trigger.value,
            "estimated_value": self.estimated_value,
            "metadata": self.metadata or {}
        }


class TaskGenerator:
    """
    任务生成器

    根据事件和上下文自动生成需要处理的任务
    """

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.client = None

        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )

    # ========== 任务生成 ==========

    async def generate_tasks(
        self,
        intent_result: IntentResult,
        content: str,
        actor_info: Dict,
        event_context: Dict = None
    ) -> List[GeneratedTask]:
        """
        根据意图和内容生成任务

        Args:
            intent_result: 意图识别结果
            content: 原始内容
            actor_info: Actor 信息
            event_context: 事件上下文

        Returns:
            生成的任务列表
        """
        tasks = []

        # 1. 基于规则生成任务
        rule_tasks = self._rule_based_generation(
            intent_result, content, actor_info, event_context
        )
        tasks.extend(rule_tasks)

        # 2. 使用 AI 补充任务
        if self.client and intent_result.intent == Intent.CONTRIBUTE:
            ai_tasks = await self._ai_task_generation(
                intent_result, content, actor_info, event_context
            )
            tasks.extend(ai_tasks)

        return tasks

    def _rule_based_generation(
        self,
        intent_result: IntentResult,
        content: str,
        actor_info: Dict,
        event_context: Dict
    ) -> List[GeneratedTask]:
        """基于规则的任务生成"""
        tasks = []

        # 提取关键信息
        trust_score = actor_info.get("trust_score", 0.5)
        contribution_value = event_context.get("estimated_value", 0) if event_context else 0
        contribution_count = actor_info.get("contribution_count", 0)

        # 规则1: 高价值贡献需要核实
        if contribution_value > 5000:
            tasks.append(GeneratedTask(
                type="verify",
                description=f"核实高价值贡献：{content[:50]}...",
                priority=80,
                required_capabilities={"审核": 0.6, "财务": 0.5},
                deadline=datetime.utcnow() + timedelta(hours=24),
                trigger=TaskTrigger.HIGH_VALUE,
                estimated_value=contribution_value,
                metadata={"reason": "高价值贡献需核实"}
            ))

        # 规则2: 低信任用户需要审核
        if trust_score < 0.3:
            tasks.append(GeneratedTask(
                type="approve",
                description=f"审核低信任用户贡献：{content[:50]}...",
                priority=70,
                required_capabilities={"审核": 0.7},
                deadline=datetime.utcnow() + timedelta(hours=48),
                trigger=TaskTrigger.LOW_TRUST,
                estimated_value=contribution_value,
                metadata={"reason": "低信任用户需审核"}
            ))

        # 规则3: 首次贡献需要验证
        if contribution_count == 0:
            tasks.append(GeneratedTask(
                type="verify",
                description=f"验证首次贡献：{content[:50]}...",
                priority=60,
                required_capabilities={"审核": 0.5},
                deadline=datetime.utcnow() + timedelta(hours=72),
                trigger=TaskTrigger.FIRST_TIME,
                estimated_value=contribution_value,
                metadata={"reason": "首次贡献需验证"}
            ))

        # 规则4: 采购贡献需要评估
        if intent_result.sub_intent == "purchase":
            # 提取金额
            amount = 0
            for entity in intent_result.entities:
                if entity.type.value == "amount":
                    amount = entity.value
                    break

            if amount > 1000:
                tasks.append(GeneratedTask(
                    type="evaluate",
                    description=f"评估采购合理性：{content[:50]}...",
                    priority=65,
                    required_capabilities={"采购": 0.6, "财务": 0.5},
                    deadline=datetime.utcnow() + timedelta(hours=24),
                    trigger=TaskTrigger.MANUAL_REQUEST,
                    estimated_value=amount * 0.3,
                    metadata={"reason": "大额采购需评估", "amount": amount}
                ))

        # 规则5: 销售贡献需要确认
        if intent_result.sub_intent == "sale":
            tasks.append(GeneratedTask(
                type="verify",
                description=f"确认销售记录：{content[:50]}...",
                priority=55,
                required_capabilities={"销售": 0.5},
                deadline=datetime.utcnow() + timedelta(hours=48),
                trigger=TaskTrigger.MANUAL_REQUEST,
                estimated_value=contribution_value,
                metadata={"reason": "销售记录需确认"}
            ))

        return tasks

    async def _ai_task_generation(
        self,
        intent_result: IntentResult,
        content: str,
        actor_info: Dict,
        event_context: Dict
    ) -> List[GeneratedTask]:
        """使用 AI 生成任务"""
        prompt = f"""你是一个企业ERP系统的任务生成引擎。根据用户贡献自动生成需要处理的任务。

用户输入：{content}
意图：{intent_result.intent.value}
子意图：{intent_result.sub_intent}
提取实体：{json.dumps([e.to_dict() for e in intent_result.entities], ensure_ascii=False)}
用户信任分：{actor_info.get("trust_score", 0.5)}
预估价值：{event_context.get("estimated_value", 0) if event_context else 0}

任务类型选项：
- verify: 核实（核实信息真实性）
- approve: 审批（需要上级批准）
- evaluate: 评估（评估合理性/价值）
- execute: 执行（需要实际操作）
- review: 审核（事后审查）

判断是否需要生成任务，如果需要，按以下JSON格式返回：
{{
    "need_tasks": true/false,
    "tasks": [
        {{
            "type": "任务类型",
            "description": "任务描述",
            "priority": 0-100,
            "required_capabilities": {{"能力名": 最低要求}},
            "deadline_hours": 小时数,
            "reason": "生成原因"
        }}
    ]
}}

如果不需要生成任务，返回 {{"need_tasks": false}}。
只返回JSON，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            if not result.get("need_tasks", False):
                return []

            tasks = []
            for t in result.get("tasks", []):
                try:
                    deadline_hours = t.get("deadline_hours", 24)
                    tasks.append(GeneratedTask(
                        type=t.get("type", "verify"),
                        description=t.get("description", ""),
                        priority=t.get("priority", 50),
                        required_capabilities=t.get("required_capabilities", {}),
                        deadline=datetime.utcnow() + timedelta(hours=deadline_hours),
                        trigger=TaskTrigger.MANUAL_REQUEST,
                        metadata={"reason": t.get("reason", "")}
                    ))
                except Exception as e:
                    print(f"Task parse error: {e}")

            return tasks

        except Exception as e:
            print(f"AI task generation error: {e}")
            return []

    # ========== 优先级计算 ==========

    def calculate_priority(
        self,
        task_type: str,
        value: float,
        urgency: int = 0,
        trust_score: float = 0.5
    ) -> int:
        """
        计算任务优先级

        考虑因素：
        1. 任务类型权重
        2. 价值权重
        3. 紧急程度
        4. 用户信任分

        Returns:
            优先级 0-100
        """
        # 类型权重
        type_weights = {
            "verify": 60,
            "approve": 70,
            "execute": 50,
            "evaluate": 55,
            "review": 45
        }
        type_score = type_weights.get(task_type, 50)

        # 价值权重 (0-20分)
        value_score = min(20, value / 1000)

        # 紧急程度 (0-10分)
        urgency_score = min(10, urgency)

        # 信任分影响 (低信任分增加优先级，最多+10分)
        trust_factor = (0.5 - trust_score) * 20 if trust_score < 0.5 else 0

        total = type_score + value_score + urgency_score + trust_factor
        return min(100, max(0, int(total)))

    # ========== 超时处理 ==========

    def check_timeout(self, task: Dict, reassign: bool = True) -> Optional[Dict]:
        """
        检查任务是否超时

        Args:
            task: 任务信息
            reassign: 是否自动重新分配

        Returns:
            如果超时，返回重分配信息
        """
        deadline = task.get("deadline")
        status = task.get("status")

        if not deadline or status in ["completed", "cancelled"]:
            return None

        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)

        if datetime.utcnow() > deadline:
            return {
                "task_id": task.get("id"),
                "timeout": True,
                "reassign": reassign,
                "original_assignee": task.get("assigned_to"),
                "reason": "任务超时"
            }

        return None


# 单例实例
_task_generator: Optional[TaskGenerator] = None


def get_task_generator() -> TaskGenerator:
    """获取任务生成器实例"""
    global _task_generator
    if _task_generator is None:
        _task_generator = TaskGenerator()
    return _task_generator
