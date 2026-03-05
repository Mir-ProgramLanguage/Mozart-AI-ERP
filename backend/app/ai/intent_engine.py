"""
意图理解引擎
"""

from app.services.ai_service import AIService


class IntentEngine:
    """意图理解引擎"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def understand(self, text: str) -> dict:
        """
        理解用户输入的意图
        
        Args:
            text: 用户输入文本
            
        Returns:
            {
                "intent": "record/query/approve/question/report",
                "confidence": 0.95,
                "keywords": [...]
            }
        """
        prompt = f"""
分析以下文本的意图。

文本：{text}

请判断主要意图：
- record: 记录事件（采购、销售、支出等）
- query: 查询信息
- approve: 审批确认
- question: 提出问题
- report: 生成报告

返回JSON格式：
{{
  "intent": "意图类型",
  "confidence": 0.0-1.0的置信度,
  "keywords": ["关键词列表"]
}}
"""
        
        response = await self.ai_service.chat(prompt)
        return self._parse_response(response)
    
    async def understand_query(self, question: str) -> dict:
        """
        理解查询意图
        
        Args:
            question: 问题
            
        Returns:
            {
                "entity": "purchase/sales/expense",
                "aggregation": "sum/count/average",
                "time_range": "today/this_week/this_month",
                "filters": {...}
            }
        """
        prompt = f"""
分析以下查询问题的意图。

问题：{question}

返回JSON格式：
{{
  "entity": "查询的实体类型",
  "aggregation": "聚合方式(sum/count/average)",
  "time_range": "时间范围",
  "filters": {{其他筛选条件}}
}}
"""
        
        response = await self.ai_service.chat(prompt)
        return self._parse_response(response)
    
    async def generate_answer(self, question: str, events: list, context: dict = None) -> dict:
        """
        生成自然语言回答
        
        Args:
            question: 问题
            events: 相关事件列表
            context: 额外上下文
            
        Returns:
            {
                "text": "回答文本",
                "data": {...}
            }
        """
        # 格式化事件
        events_text = "\n".join([
            f"- {e.content}" for e in events[:10]
        ])
        
        prompt = f"""
基于以下信息回答问题。

问题：{question}

相关事件：
{events_text}

额外数据：
{context or '无'}

要求：
1. 用自然、友好的语言回答
2. 提供具体的数字和数据
3. 必要时给出建议
4. 简洁明了，不超过100字

返回JSON格式：
{{
  "text": "回答文本",
  "data": {{关键数据}}
}}
"""
        
        response = await self.ai_service.chat(prompt)
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        """解析AI响应"""
        import json
        
        try:
            # 提取JSON部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except:
            # 默认返回
            return {
                "intent": "unknown",
                "confidence": 0.0
            }
