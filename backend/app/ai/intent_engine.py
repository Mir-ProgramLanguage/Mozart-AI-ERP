"""
意图理解引擎 - Intent Engine

核心功能：
1. 意图分类（contribute/record/query/approve/question）
2. 实体提取（金额、人员、物品、时间等）
3. 置信度评估
4. 上下文理解
"""
from enum import Enum
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re
import os

# DeepSeek API
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class Intent(str, Enum):
    """意图类型"""
    CONTRIBUTE = "contribute"       # 提供贡献
    RECORD = "record"               # 记录事件
    QUERY = "query"                 # 查询信息
    APPROVE = "approve"             # 审批确认
    QUESTION = "question"           # 提出问题
    COMMAND = "command"             # 执行命令
    CHAT = "chat"                   # 普通对话
    UNKNOWN = "unknown"             # 未知


class EntityType(str, Enum):
    """实体类型"""
    AMOUNT = "amount"               # 金额
    PERSON = "person"               # 人员
    ITEM = "item"                   # 物品
    DATE = "date"                   # 日期
    TIME = "time"                   # 时间
    LOCATION = "location"           # 地点
    ORGANIZATION = "organization"   # 组织
    QUANTITY = "quantity"           # 数量
    PHONE = "phone"                 # 电话
    EMAIL = "email"                 # 邮箱


@dataclass
class Entity:
    """提取的实体"""
    type: EntityType
    value: Any
    raw_text: str
    confidence: float = 1.0

    def to_dict(self):
        return {
            "type": self.type.value,
            "value": self.value,
            "raw_text": self.raw_text,
            "confidence": self.confidence
        }


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: Intent
    confidence: float
    entities: List[Entity] = field(default_factory=list)
    sub_intent: Optional[str] = None
    reasoning: str = ""
    raw_response: str = ""

    def to_dict(self):
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "entities": [e.to_dict() for e in self.entities],
            "sub_intent": self.sub_intent,
            "reasoning": self.reasoning
        }


class IntentEngine:
    """
    意图理解引擎

    使用规则 + AI 混合方式识别意图
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

    # ========== 意图识别 ==========

    async def understand(self, text: str, context: Dict = None) -> IntentResult:
        """
        理解用户输入

        Args:
            text: 用户输入文本
            context: 上下文信息

        Returns:
            IntentResult: 意图识别结果
        """
        # 1. 先用规则快速识别
        rule_result = self._rule_based_intent(text)
        if rule_result.confidence > 0.9:
            # 规则高置信度，直接返回
            return rule_result

        # 2. 使用 AI 深度理解
        if self.client:
            ai_result = await self._ai_intent_recognition(text, context)
            # 如果 AI 置信度更高，使用 AI 结果
            if ai_result.confidence > rule_result.confidence:
                return ai_result

        return rule_result

    def _rule_based_intent(self, text: str) -> IntentResult:
        """基于规则的意图识别"""
        text_lower = text.lower()

        # 贡献相关关键词
        contribute_patterns = [
            r"买了?(\d+).*?(元|块)",
            r"卖了?(\d+).*?(元|块)",
            r"节省?(\d+)",
            r"推荐.*?(人才|员工)",
            r"发现.*?(机会|问题|风险)",
            r"完成.*?任务",
            r"贡献",
        ]

        # 查询相关关键词
        query_patterns = [
            r"(多少|几个|什么|哪些|怎样|如何)",
            r"(查询|查看|统计|报表|分析)",
            r"(本月|今天|最近).*(花费|收入|支出)",
            r"排行榜",
        ]

        # 审批相关关键词
        approve_patterns = [
            r"(同意|批准|通过|确认)",
            r"(拒绝|驳回|不同意)",
            r"(审核|审批)",
        ]

        # 问题相关关键词
        question_patterns = [
            r"^(为什么|怎么会|是不是|能否|可以)",
            r"\?$",  # 以问号结尾
        ]

        # 命令相关关键词
        command_patterns = [
            r"^(创建|添加|删除|修改|更新)",
            r"(设置|配置)",
        ]

        # 检查各类型
        for pattern in contribute_patterns:
            if re.search(pattern, text):
                entities = self._extract_entities(text)
                return IntentResult(
                    intent=Intent.CONTRIBUTE,
                    confidence=0.85,
                    entities=entities,
                    reasoning="匹配贡献模式"
                )

        for pattern in query_patterns:
            if re.search(pattern, text):
                return IntentResult(
                    intent=Intent.QUERY,
                    confidence=0.8,
                    reasoning="匹配查询模式"
                )

        for pattern in approve_patterns:
            if re.search(pattern, text):
                return IntentResult(
                    intent=Intent.APPROVE,
                    confidence=0.85,
                    reasoning="匹配审批模式"
                )

        for pattern in question_patterns:
            if re.search(pattern, text):
                return IntentResult(
                    intent=Intent.QUESTION,
                    confidence=0.75,
                    reasoning="匹配问题模式"
                )

        for pattern in command_patterns:
            if re.search(pattern, text):
                return IntentResult(
                    intent=Intent.COMMAND,
                    confidence=0.8,
                    reasoning="匹配命令模式"
                )

        # 默认为对话
        return IntentResult(
            intent=Intent.CHAT,
            confidence=0.5,
            reasoning="未匹配特定模式"
        )

    async def _ai_intent_recognition(
        self,
        text: str,
        context: Dict = None
    ) -> IntentResult:
        """使用 AI 进行意图识别"""
        prompt = f"""你是一个企业ERP系统的意图识别引擎。分析用户输入，识别意图并提取实体。

用户输入：{text}

上下文：{json.dumps(context, ensure_ascii=False) if context else '无'}

请按以下JSON格式返回：
{{
    "intent": "contribute/record/query/approve/question/command/chat",
    "sub_intent": "具体子意图，如 purchase/sale/recruitment 等",
    "confidence": 0.0-1.0,
    "entities": [
        {{"type": "amount/person/item/date/quantity/location", "value": "提取的值", "raw_text": "原文"}}
    ],
    "reasoning": "判断理由"
}}

只返回JSON，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            # 解析实体
            entities = []
            for e in result.get("entities", []):
                try:
                    entity_type = EntityType(e.get("type", "item"))
                    entities.append(Entity(
                        type=entity_type,
                        value=e.get("value"),
                        raw_text=e.get("raw_text", ""),
                        confidence=0.9
                    ))
                except ValueError:
                    pass

            # 解析意图
            try:
                intent = Intent(result.get("intent", "unknown"))
            except ValueError:
                intent = Intent.UNKNOWN

            return IntentResult(
                intent=intent,
                confidence=result.get("confidence", 0.5),
                entities=entities,
                sub_intent=result.get("sub_intent"),
                reasoning=result.get("reasoning", ""),
                raw_response=result_text
            )

        except Exception as e:
            print(f"AI intent recognition error: {e}")
            return IntentResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
                reasoning=f"AI识别失败: {str(e)}"
            )

    # ========== 实体提取 ==========

    def _extract_entities(self, text: str) -> List[Entity]:
        """从文本中提取实体"""
        entities = []

        # 提取金额
        amount_patterns = [
            r"(\d+(?:\.\d+)?)\s*(元|块|万|千元)",
            r"(¥|￥)\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*块钱",
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                amount_str = match[0] if isinstance(match, tuple) else match
                try:
                    amount = float(amount_str)
                    entities.append(Entity(
                        type=EntityType.AMOUNT,
                        value=amount,
                        raw_text=str(match),
                        confidence=0.95
                    ))
                except ValueError:
                    pass

        # 提取数量
        quantity_patterns = [
            r"(\d+)\s*(个|件|斤|kg|吨|箱|盒|台)",
            r"(\d+)\s*人",
        ]
        for pattern in quantity_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append(Entity(
                    type=EntityType.QUANTITY,
                    value=int(match[0]),
                    raw_text=str(match),
                    confidence=0.9
                ))

        # 提取日期
        date_patterns = [
            r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)",
            r"(今天|昨天|明天|本周|上周|下周|本月|上月)",
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append(Entity(
                    type=EntityType.DATE,
                    value=match,
                    raw_text=match,
                    confidence=0.85
                ))

        return entities

    # ========== 意图处理 ==========

    def get_contribution_type(self, text: str, intent_result: IntentResult) -> str:
        """根据文本和意图确定贡献类型"""
        text_lower = text.lower()

        # 销售
        if any(kw in text_lower for kw in ["卖", "销售", "成交", "客户"]):
            return "sale"

        # 采购
        if any(kw in text_lower for kw in ["买", "采购", "供应商"]):
            return "purchase"

        # 人才推荐
        if any(kw in text_lower for kw in ["推荐", "人才", "招聘", "面试"]):
            return "recruitment"

        # 风险预警
        if any(kw in text_lower for kw in ["风险", "问题", "预警", "发现"]):
            return "risk_warning"

        # 知识分享
        if any(kw in text_lower for kw in ["文档", "分享", "教程", "培训"]):
            return "knowledge_sharing"

        # 默认
        return "general"


# 单例实例
_intent_engine: Optional[IntentEngine] = None


def get_intent_engine() -> IntentEngine:
    """获取意图引擎实例"""
    global _intent_engine
    if _intent_engine is None:
        _intent_engine = IntentEngine()
    return _intent_engine
