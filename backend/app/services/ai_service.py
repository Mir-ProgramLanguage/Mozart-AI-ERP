"""
AI服务 - 原生AI ERP的大脑

负责：
1. 理解用户输入的意图
2. 提取结构化信息
3. 自然语言查询理解
4. 生成自然语言回答
"""

from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings


class AIService:
    """DeepSeek AI服务"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    async def understand_input(self, text: str) -> Dict[str, Any]:
        """
        理解用户输入

        输入："今天采购了20斤土豆35元一斤供应商张三"

        输出：
        {
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
        }
        """
        prompt = f"""
你是一个企业管理助手，负责理解用户的业务输入。

用户输入：{text}

请分析这段输入，返回JSON格式：
{{
    "intent": "意图类型（purchase采购/sales销售/expense支出/query查询/other其他）",
    "confidence": 0.0-1.0的置信度,
    "extracted": {{
        // 根据意图提取相关字段
        // 采购：item, quantity, unit, unit_price, total_amount, supplier, date
        // 销售：revenue, customer_count, date
        // 支出：category, amount, description, date
    }}
}}

注意：
1. 如果没有明确日期，date使用"今天"
2. 如果只有总价没有单价，计算单价
3. 如果信息不完整，extracted中对应字段设为null
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=settings.DEEPSEEK_TEMPERATURE,
        )

        # TODO: 解析响应并返回
        return {}

    async def understand_query(self, query: str) -> Dict[str, Any]:
        """
        理解用户查询

        输入："本月采购了多少钱？"

        输出：
        {
            "intent": "aggregate_query",
            "entity": "purchase",
            "aggregation": "sum",
            "field": "total_amount",
            "time_range": {
                "type": "month",
                "value": "current"
            },
            "filters": {}
        }
        """
        prompt = f"""
你是一个数据查询助手，负责理解用户的查询需求。

用户查询：{query}

请分析这个查询，返回JSON格式：
{{
    "intent": "查询类型（aggregate_query聚合查询/detail_query明细查询/comparison_query对比查询/trend_query趋势查询）",
    "entity": "查询实体（purchase采购/sales销售/expense支出）",
    "aggregation": "聚合方式（sum求和/avg平均/count计数/max最大/min最小）",
    "field": "查询字段（total_amount金额/quantity数量等）",
    "time_range": {{
        "type": "时间类型（day/week/month/year）",
        "value": "时间值（current当前/last上一个/specific具体日期）"
    }},
    "filters": {{
        // 其他筛选条件，如供应商、商品名等
    }}
}}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,  # 查询理解需要更精确
        )

        # TODO: 解析响应并返回
        return {}

    async def generate_answer(
        self, query: str, data: Dict[str, Any], events: List[Dict]
    ) -> str:
        """
        生成自然语言回答

        输入：
        - query: "本月采购了多少钱？"
        - data: {"total_amount": 15230, "count": 23}
        - events: [相关事件列表]

        输出：
        "本月（2026年3月）共采购了15,230元，包括23笔采购记录。
        主要采购项目包括：土豆（5次）、白菜（3次）、猪肉（8次）等。"
        """
        prompt = f"""
你是一个企业管理助手，负责用自然语言回答用户的查询。

用户问题：{query}

查询结果数据：
{data}

相关事件：
{events[:5]}  # 只展示前5条

请用自然、专业的语言回答用户的问题，要求：
1. 直接回答问题，不要重复问题
2. 包含关键数字和统计信息
3. 如果有趋势或异常，主动指出
4. 语言简洁，不超过3句话
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return response.choices[0].message.content
