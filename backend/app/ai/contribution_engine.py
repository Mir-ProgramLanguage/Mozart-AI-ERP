"""
贡献评估引擎

核心功能：
1. 识别贡献类型
2. 评估贡献价值
3. 计算置信度
4. 生成价值计算依据
"""

from typing import Dict, List, Tuple
from decimal import Decimal
from datetime import datetime
from app.services.ai_service import AIService


class ContributionType:
    """贡献类型定义"""
    
    # 业务类
    SALES_OPPORTUNITY = "sales_opportunity"        # 销售线索
    SALES_CLOSE = "sales_close"                    # 成交销售
    PURCHASE_OPPORTUNITY = "purchase_opportunity"  # 采购机会
    PURCHASE_SAVING = "purchase_saving"            # 采购节省
    PRODUCT_DEVELOP = "product_develop"            # 产品开发
    
    # 人才类
    TALENT_INTRODUCE = "talent_introduce"          # 人才推荐
    INTERVIEW_PARTICIPATE = "interview_participate"  # 参与面试
    TRAINING_PROVIDE = "training_provide"          # 提供培训
    
    # 知识类
    KNOWLEDGE_SHARE = "knowledge_share"            # 知识分享
    DOCUMENT_WRITE = "document_write"              # 文档编写
    PROCESS_OPTIMIZE = "process_optimize"          # 流程优化
    
    # 风险类
    RISK_ALERT = "risk_alert"                      # 风险预警
    ISSUE_DISCOVER = "issue_discover"              # 问题发现


class ContributionEvaluator:
    """贡献评估引擎"""
    
    def __init__(self):
        self.ai_service = AIService()
        
        # 贡献价值参数
        self.value_params = {
            # 采购节省：贡献者获得节省金额的30%作为贡献值
            "purchase_saving": {
                "share_rate": 0.30,
                "min_value": 10,
            },
            
            # 销售机会：预估销售额的5%作为贡献值
            "sales_opportunity": {
                "estimate_rate": 0.05,
                "min_value": 50,
            },
            
            # 销售成交：销售额 × 利润率 × 50%
            "sales_close": {
                "profit_share": 0.50,
                "default_margin": 0.20,
                "min_value": 100,
            },
            
            # 人才推荐：根据人才等级
            "talent_introduce": {
                "senior": 10000,
                "middle": 5000,
                "normal": 2000,
                "min_value": 500,
            },
            
            # 风险预警：规避损失的20%
            "risk_alert": {
                "share_rate": 0.20,
                "min_value": 100,
            },
            
            # 产品开发：时薪 × 时间 × 难度
            "product_develop": {
                "hourly_rate": 100,
                "min_value": 50,
            },
            
            # 知识分享：阅读量 × 单价
            "knowledge_share": {
                "view_value": 10,  # 每次阅读价值
                "min_value": 10,
            },
        }
    
    async def evaluate(
        self, 
        content: str, 
        context: Dict = None
    ) -> Dict:
        """
        评估贡献价值
        
        Args:
            content: 贡献内容
            context: 额外上下文（如附件信息等）
            
        Returns:
            {
                "contribution_type": 类型,
                "estimated_value": 预估价值,
                "confidence": 置信度,
                "calculation_basis": 计算依据,
                "entities": 提取的实体
            }
        """
        
        # 1. AI识别贡献类型和提取实体
        analysis = await self._analyze_contribution(content)
        
        # 2. 评估价值
        value_result = await self._calculate_value(
            contribution_type=analysis["contribution_type"],
            entities=analysis["entities"],
            content=content
        )
        
        return {
            "contribution_type": analysis["contribution_type"],
            "estimated_value": value_result["value"],
            "confidence": analysis["confidence"],
            "calculation_basis": value_result["basis"],
            "entities": analysis["entities"]
        }
    
    async def _analyze_contribution(self, content: str) -> Dict:
        """AI分析贡献类型和提取实体"""
        
        prompt = f"""
分析以下内容，识别贡献类型并提取关键实体。

内容：{content}

贡献类型：
- sales_opportunity: 提供销售线索
- sales_close: 成交销售
- purchase_opportunity: 发现采购机会
- purchase_saving: 采购节省成本
- product_develop: 产品开发
- talent_introduce: 推荐人才
- knowledge_share: 分享知识
- risk_alert: 风险预警
- process_optimize: 流程优化

请返回JSON格式：
{{
  "contribution_type": "类型",
  "confidence": 0.0-1.0,
  "entities": {{
    "item": "商品名称",
    "price": 价格,
    "market_price": 市场价,
    "saving_amount": 节省金额,
    "sales_amount": 销售金额,
    "profit_margin": 利润率,
    "quantity": 数量,
    "talent_level": "人才等级(senior/middle/normal)",
    "hired": 是否录用,
    "risk_type": "风险类型",
    "potential_loss": 潜在损失,
    "time_spent": 投入时间(小时),
    "difficulty": 难度系数(1.0-3.0)
  }}
}}

注意：
1. 只提取相关的实体，无关的不要返回
2. 价格和金额必须是数字
3. confidence要基于信息完整度评估
"""
        
        response = await self.ai_service.chat(prompt)
        return self._parse_json_response(response)
    
    async def _calculate_value(
        self, 
        contribution_type: str, 
        entities: Dict,
        content: str
    ) -> Dict:
        """计算贡献价值"""
        
        value = Decimal("0")
        basis = {}
        
        # 根据类型计算
        if contribution_type == ContributionType.PURCHASE_SAVING:
            value, basis = self._calc_purchase_saving(entities)
        
        elif contribution_type == ContributionType.SALES_OPPORTUNITY:
            value, basis = self._calc_sales_opportunity(entities)
        
        elif contribution_type == ContributionType.SALES_CLOSE:
            value, basis = self._calc_sales_close(entities)
        
        elif contribution_type == ContributionType.TALENT_INTRODUCE:
            value, basis = self._calc_talent_introduce(entities)
        
        elif contribution_type == ContributionType.RISK_ALERT:
            value, basis = self._calc_risk_alert(entities)
        
        elif contribution_type == ContributionType.PRODUCT_DEVELOP:
            value, basis = self._calc_product_develop(entities)
        
        elif contribution_type == ContributionType.KNOWLEDGE_SHARE:
            value, basis = self._calc_knowledge_share(entities)
        
        # 确保最小值
        params = self.value_params.get(contribution_type, {})
        min_value = params.get("min_value", 10)
        value = max(value, Decimal(str(min_value)))
        
        return {
            "value": float(value),
            "basis": basis
        }
    
    def _calc_purchase_saving(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算采购节省贡献
        
        公式：节省金额 × 30%
        """
        saving_amount = Decimal(str(entities.get("saving_amount", 0)))
        share_rate = Decimal(str(self.value_params["purchase_saving"]["share_rate"]))
        
        value = saving_amount * share_rate
        
        basis = {
            "type": "purchase_saving",
            "formula": f"{saving_amount} × {share_rate} = {value}",
            "saving_amount": float(saving_amount),
            "share_rate": float(share_rate)
        }
        
        return value, basis
    
    def _calc_sales_opportunity(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算销售机会贡献
        
        公式：预估销售额 × 5%
        """
        sales_amount = Decimal(str(entities.get("sales_amount", 0)))
        estimate_rate = Decimal(str(self.value_params["sales_opportunity"]["estimate_rate"]))
        
        value = sales_amount * estimate_rate
        
        basis = {
            "type": "sales_opportunity",
            "formula": f"{sales_amount} × {estimate_rate} = {value}",
            "sales_amount": float(sales_amount),
            "estimate_rate": float(estimate_rate),
            "note": "仅线索贡献，成交后会追加贡献值"
        }
        
        return value, basis
    
    def _calc_sales_close(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算销售成交贡献
        
        公式：销售额 × 利润率 × 50%
        """
        sales_amount = Decimal(str(entities.get("sales_amount", 0)))
        profit_margin = Decimal(str(
            entities.get("profit_margin", 
                        self.value_params["sales_close"]["default_margin"])
        ))
        profit_share = Decimal(str(self.value_params["sales_close"]["profit_share"]))
        
        profit = sales_amount * profit_margin
        value = profit * profit_share
        
        basis = {
            "type": "sales_close",
            "formula": f"{sales_amount} × {profit_margin} × {profit_share} = {value}",
            "sales_amount": float(sales_amount),
            "profit_margin": float(profit_margin),
            "profit": float(profit),
            "profit_share": float(profit_share)
        }
        
        return value, basis
    
    def _calc_talent_introduce(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算人才推荐贡献
        
        根据人才等级固定奖励
        """
        talent_level = entities.get("talent_level", "normal")
        hired = entities.get("hired", False)
        
        # 未录用无价值
        if not hired:
            return Decimal("0"), {
                "type": "talent_introduce",
                "note": "人才未录用，暂无贡献值",
                "status": "pending"
            }
        
        # 根据等级确定奖励
        rewards = self.value_params["talent_introduce"]
        reward = rewards.get(talent_level, rewards["normal"])
        
        value = Decimal(str(reward))
        
        basis = {
            "type": "talent_introduce",
            "formula": f"人才等级 {talent_level} = {reward}元",
            "talent_level": talent_level,
            "hired": hired
        }
        
        return value, basis
    
    def _calc_risk_alert(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算风险预警贡献
        
        公式：潜在损失 × 20%
        """
        potential_loss = Decimal(str(entities.get("potential_loss", 0)))
        share_rate = Decimal(str(self.value_params["risk_alert"]["share_rate"]))
        
        value = potential_loss * share_rate
        
        basis = {
            "type": "risk_alert",
            "formula": f"{potential_loss} × {share_rate} = {value}",
            "potential_loss": float(potential_loss),
            "share_rate": float(share_rate)
        }
        
        return value, basis
    
    def _calc_product_develop(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算产品开发贡献
        
        公式：时薪 × 时间 × 难度系数
        """
        time_spent = Decimal(str(entities.get("time_spent", 0)))
        difficulty = Decimal(str(entities.get("difficulty", 1.0)))
        hourly_rate = Decimal(str(self.value_params["product_develop"]["hourly_rate"]))
        
        value = hourly_rate * time_spent * difficulty
        
        basis = {
            "type": "product_develop",
            "formula": f"{hourly_rate} × {time_spent} × {difficulty} = {value}",
            "time_spent": float(time_spent),
            "difficulty": float(difficulty),
            "hourly_rate": float(hourly_rate)
        }
        
        return value, basis
    
    def _calc_knowledge_share(self, entities: Dict) -> Tuple[Decimal, Dict]:
        """
        计算知识分享贡献
        
        公式：预估阅读量 × 10元
        """
        # 由于是分享，阅读量需要时间积累
        # 这里先给一个初始值，后续会根据实际阅读量调整
        estimated_views = Decimal(str(entities.get("estimated_views", 10)))
        view_value = Decimal(str(self.value_params["knowledge_share"]["view_value"]))
        
        value = estimated_views * view_value
        
        basis = {
            "type": "knowledge_share",
            "formula": f"{estimated_views}(预估阅读) × {view_value} = {value}",
            "estimated_views": float(estimated_views),
            "view_value": float(view_value),
            "note": "初始贡献值，后续会根据实际阅读量调整"
        }
        
        return value, basis
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析AI返回的JSON"""
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
                "contribution_type": "unknown",
                "confidence": 0.0,
                "entities": {}
            }


# 全局贡献评估器
contribution_evaluator = ContributionEvaluator()
