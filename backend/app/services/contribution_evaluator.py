"""
贡献评估引擎 (Contribution Evaluator)

负责评估每个贡献事件的价值：
1. 根据贡献类型确定评估方法
2. 提取关键实体（金额、数量等）
3. 计算贡献价值
4. 返回置信度
"""

import json
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime
from openai import OpenAI

from app.config import settings
from app.models.contribution import Event, ContributionStatus


class ContributionType:
    """贡献类型常量"""

    # ===== 业务类贡献 =====
    SALES_OPPORTUNITY = "sales_opportunity"       # 提供销售线索
    SALES_CLOSE = "sales_close"                    # 完成销售
    CUSTOMER_RETENTION = "customer_retention"      # 客户留存

    PURCHASE_OPPORTUNITY = "purchase_opportunity"  # 发现采购机会
    PURCHASE_SAVING = "purchase_saving"            # 采购节省
    SUPPLIER_QUALITY = "supplier_quality"          # 供应商质量

    PRODUCT_DEVELOP = "product_develop"            # 产品开发
    PRODUCT_OPTIMIZE = "product_optimize"          # 产品优化
    BUG_FIX = "bug_fix"                            # 问题修复

    # ===== 人才类贡献 =====
    TALENT_INTRODUCE = "talent_introduce"          # 人才推荐
    INTERVIEW_PARTICIPATE = "interview_participate"  # 参与面试
    TRAINING_PROVIDE = "training_provide"          # 提供培训
    MENTORING = "mentoring"                        # 指导带教

    # ===== 资源类贡献 =====
    RESOURCE_PROVIDE = "resource_provide"          # 提供资源
    PARTNER_INTRODUCE = "partner_introduce"        # 引入合作伙伴
    INFORMATION_SHARE = "information_share"        # 信息分享

    # ===== 知识类贡献 =====
    KNOWLEDGE_SHARE = "knowledge_share"            # 知识分享
    DOCUMENT_WRITE = "document_write"              # 文档编写
    PROCESS_OPTIMIZE = "process_optimize"          # 流程优化
    TOOL_DEVELOP = "tool_develop"                  # 工具开发

    # ===== 风险类贡献 =====
    RISK_ALERT = "risk_alert"                      # 风险预警
    ISSUE_DISCOVER = "issue_discover"              # 问题发现
    CRISIS_HANDLE = "crisis_handle"                # 危机处理

    # ===== 通用贡献 =====
    GENERAL = "general"                            # 通用贡献


class ContributionEvaluator:
    """
    贡献评估引擎
    
    核心算法：
    - 销售类：销售额 × 利润率 × 贡献比例
    - 采购类：节省金额 × 分享比例
    - 人才类：固定奖励 + 人才等级加成
    - 风险类：规避损失 × 分享比例
    """

    # 回报杠杆配置
    REWARD_RATES = {
        ContributionType.SALES_CLOSE: {
            "profit_share": 0.5,     # 利润的50%
            "default_margin": 0.2,   # 默认利润率20%
        },
        ContributionType.PURCHASE_SAVING: {
            "saving_share": 0.3,     # 节省金额的30%
        },
        ContributionType.TALENT_INTRODUCE: {
            "senior": 10000,         # 高级人才奖励
            "middle": 5000,          # 中级人才奖励
            "normal": 2000,          # 普通人才奖励
        },
        ContributionType.RISK_ALERT: {
            "loss_share": 0.2,       # 规避损失的20%
        },
        ContributionType.PRODUCT_DEVELOP: {
            "hourly_rate": 100,      # 基础时薪
        }
    }

    def __init__(self):
        self.llm = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.model = settings.DEEPSEEK_MODEL

    async def evaluate(self, event: Event) -> Dict[str, Any]:
        """
        评估贡献价值
        
        返回：
        {
            "value": 贡献价值,
            "confidence": 置信度,
            "calculation_basis": 计算依据,
            "contribution_type": 贡献类型
        }
        """
        # 1. 识别贡献类型
        contribution_type, type_confidence = await self._identify_contribution_type(event)
        
        # 2. 提取关键实体
        entities = await self._extract_entities(event, contribution_type)
        
        # 3. 计算价值
        value, value_confidence, calculation = await self._calculate_value(
            contribution_type, entities
        )
        
        # 4. 综合置信度
        confidence = (type_confidence + value_confidence) / 2
        
        return {
            "value": value,
            "confidence": confidence,
            "calculation_basis": calculation,
            "contribution_type": contribution_type,
            "entities": entities
        }

    async def _identify_contribution_type(self, event: Event) -> Tuple[str, float]:
        """
        识别贡献类型
        
        使用AI理解事件内容，判断贡献类型
        """
        prompt = f"""
分析以下贡献事件，判断贡献类型。

事件内容：{event.content}

贡献类型列表：
- sales_opportunity: 提供销售线索
- sales_close: 完成销售
- purchase_opportunity: 发现采购机会
- purchase_saving: 采购节省
- product_develop: 产品开发
- product_optimize: 产品优化
- talent_introduce: 人才推荐
- knowledge_share: 知识分享
- risk_alert: 风险预警
- general: 通用贡献

请返回JSON：
{{
    "type": "贡献类型",
    "confidence": 0.0-1.0
}}
"""
        try:
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("type", ContributionType.GENERAL), result.get("confidence", 0.5)
        except Exception as e:
            return ContributionType.GENERAL, 0.5

    async def _extract_entities(
        self, 
        event: Event, 
        contribution_type: str
    ) -> Dict[str, Any]:
        """
        提取关键实体
        
        根据贡献类型提取不同的实体：
        - 销售：销售金额、客户、产品
        - 采购：节省金额、供应商、商品
        - 人才：人才姓名、等级、岗位
        """
        prompt = f"""
从以下文本中提取关键信息。

文本：{event.content}
贡献类型：{contribution_type}

请提取相关信息，返回JSON格式。
示例：
- 销售：{{"amount": 10000, "customer": "XX公司", "product": "XX产品"}}
- 采购节省：{{"saving_amount": 500, "supplier": "张三", "item": "土豆"}}
- 人才推荐：{{"talent_name": "李四", "level": "senior", "position": "开发工程师"}}

请返回JSON：
{{
    "entities": {{}}
}}
"""
        try:
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("entities", {})
        except:
            return {}

    async def _calculate_value(
        self,
        contribution_type: str,
        entities: Dict[str, Any]
    ) -> Tuple[Decimal, float, Dict]:
        """
        计算贡献价值
        
        返回：(价值, 置信度, 计算过程)
        """
        value = Decimal("0")
        confidence = 0.5
        calculation = {"method": contribution_type}

        # 销售类贡献
        if contribution_type == ContributionType.SALES_CLOSE:
            amount = Decimal(str(entities.get("amount", 0)))
            margin = Decimal(str(entities.get("profit_margin", 0.2)))
            rate = Decimal(str(self.REWARD_RATES[ContributionType.SALES_CLOSE]["profit_share"]))
            
            profit = amount * margin
            value = profit * rate
            confidence = 0.9 if amount > 0 else 0.3
            
            calculation = {
                "method": "销售贡献",
                "formula": "销售额 × 利润率 × 贡献比例",
                "sales_amount": float(amount),
                "profit_margin": float(margin),
                "share_rate": float(rate),
                "result": float(value)
            }

        # 采购节省
        elif contribution_type == ContributionType.PURCHASE_SAVING:
            saving = Decimal(str(entities.get("saving_amount", 0)))
            rate = Decimal(str(self.REWARD_RATES[ContributionType.PURCHASE_SAVING]["saving_share"]))
            
            value = saving * rate
            confidence = 0.9 if saving > 0 else 0.3
            
            calculation = {
                "method": "采购节省",
                "formula": "节省金额 × 分享比例",
                "saving_amount": float(saving),
                "share_rate": float(rate),
                "result": float(value)
            }

        # 人才推荐
        elif contribution_type == ContributionType.TALENT_INTRODUCE:
            level = entities.get("level", "normal")
            hired = entities.get("hired", False)
            
            if hired:
                rewards = self.REWARD_RATES[ContributionType.TALENT_INTRODUCE]
                value = Decimal(str(rewards.get(level, rewards["normal"])))
                confidence = 0.95
            else:
                value = Decimal("0")
                confidence = 0.5
            
            calculation = {
                "method": "人才推荐",
                "formula": "根据人才等级固定奖励",
                "talent_level": level,
                "hired": hired,
                "result": float(value)
            }

        # 风险预警
        elif contribution_type == ContributionType.RISK_ALERT:
            potential_loss = Decimal(str(entities.get("potential_loss", 0)))
            rate = Decimal(str(self.REWARD_RATES[ContributionType.RISK_ALERT]["loss_share"]))
            
            value = potential_loss * rate
            confidence = 0.85 if potential_loss > 0 else 0.3
            
            calculation = {
                "method": "风险预警",
                "formula": "规避损失 × 分享比例",
                "potential_loss": float(potential_loss),
                "share_rate": float(rate),
                "result": float(value)
            }

        # 产品开发
        elif contribution_type == ContributionType.PRODUCT_DEVELOP:
            hours = Decimal(str(entities.get("hours", 0)))
            difficulty = Decimal(str(entities.get("difficulty", 1.0)))
            rate = Decimal(str(self.REWARD_RATES[ContributionType.PRODUCT_DEVELOP]["hourly_rate"]))
            
            value = rate * hours * difficulty
            confidence = 0.8
            
            calculation = {
                "method": "产品开发",
                "formula": "时薪 × 时间 × 难度系数",
                "hours": float(hours),
                "difficulty": float(difficulty),
                "hourly_rate": float(rate),
                "result": float(value)
            }

        # 通用贡献（基础值）
        else:
            value = Decimal("10")  # 默认10元
            confidence = 0.5
            calculation = {
                "method": "通用贡献",
                "result": float(value)
            }

        return value, confidence, calculation

    async def verify_contribution(
        self, 
        event: Event, 
        actual_value: Decimal,
        verifier_note: str = ""
    ) -> Dict[str, Any]:
        """
        验证贡献
        
        当贡献被验证后，更新实际价值
        """
        event.actual_value = actual_value
        event.contribution_status = ContributionStatus.VERIFIED
        event.verified_at = datetime.utcnow()
        
        return {
            "event_id": str(event.id),
            "estimated_value": float(event.contribution_value) if event.contribution_value else 0,
            "actual_value": float(actual_value),
            "status": ContributionStatus.VERIFIED,
            "verifier_note": verifier_note
        }
