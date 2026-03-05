"""
能力成长引擎

核心功能：
1. 根据贡献更新能力图谱
2. 记录能力成长历史
3. 推荐能力提升路径
"""

from typing import Dict, List
from decimal import Decimal
from datetime import datetime


class CapabilityEngine:
    """能力成长引擎"""
    
    # 能力成长系数
    GROWTH_RATE = Decimal("0.0001")  # 每贡献10000，能力提升1.0
    
    # 能力上限
    MAX_CAPABILITY = Decimal("1.0")
    
    # 贡献类型到能力的映射
    CONTRIBUTION_TO_CAPABILITY = {
        "sales_opportunity": "市场洞察",
        "sales_close": "销售能力",
        "purchase_opportunity": "采购优化",
        "purchase_saving": "采购优化",
        "product_develop": "开发能力",
        "talent_introduce": "人才识别",
        "interview_participate": "面试能力",
        "knowledge_share": "知识输出",
        "document_write": "文档能力",
        "risk_alert": "风险识别",
        "process_optimize": "流程优化"
    }
    
    async def update_capability(
        self,
        current_capabilities: Dict[str, float],
        contribution_type: str,
        contribution_value: float
    ) -> Dict:
        """
        更新能力图谱
        
        Args:
            current_capabilities: 当前能力图谱
            contribution_type: 贡献类型
            contribution_value: 贡献值
            
        Returns:
            {
                "new_capabilities": 新的能力图谱,
                "growth_record": 成长记录
            }
        """
        # 1. 确定对应的能力标签
        capability = self.CONTRIBUTION_TO_CAPABILITY.get(contribution_type)
        
        if not capability:
            # 如果没有映射，不做更新
            return {
                "new_capabilities": current_capabilities,
                "growth_record": None
            }
        
        # 2. 获取当前能力分数
        current_score = Decimal(str(current_capabilities.get(capability, 0)))
        
        # 3. 计算成长值
        growth = Decimal(str(contribution_value)) * self.GROWTH_RATE
        
        # 4. 计算新分数（不超过上限）
        new_score = min(current_score + growth, self.MAX_CAPABILITY)
        
        # 5. 准备结果
        new_capabilities = current_capabilities.copy()
        new_capabilities[capability] = float(new_score)
        
        # 6. 生成成长记录
        growth_record = {
            "capability": capability,
            "previous": float(current_score),
            "current": float(new_score),
            "growth": float(new_score - current_score),
            "reason": f"{contribution_type} 贡献值 {contribution_value}",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "new_capabilities": new_capabilities,
            "growth_record": growth_record
        }
    
    async def batch_update_capabilities(
        self,
        current_capabilities: Dict[str, float],
        contributions: List[Dict]
    ) -> Dict:
        """
        批量更新能力图谱
        
        Args:
            current_capabilities: 当前能力图谱
            contributions: 贡献列表 [{type, value}, ...]
            
        Returns:
            {
                "new_capabilities": 新能力图谱,
                "growth_records": 成长记录列表
            }
        """
        new_capabilities = current_capabilities.copy()
        growth_records = []
        
        for contribution in contributions:
            result = await self.update_capability(
                current_capabilities=new_capabilities,
                contribution_type=contribution["type"],
                contribution_value=contribution["value"]
            )
            
            new_capabilities = result["new_capabilities"]
            if result["growth_record"]:
                growth_records.append(result["growth_record"])
        
        return {
            "new_capabilities": new_capabilities,
            "growth_records": growth_records
        }
    
    def recommend_improvement(
        self,
        capabilities: Dict[str, float],
        target_roles: List[str] = None
    ) -> List[Dict]:
        """
        推荐能力提升路径
        
        Args:
            capabilities: 当前能力图谱
            target_roles: 目标角色
            
        Returns:
            推荐的提升路径
        """
        # 找出较弱的能力
        weak_capabilities = [
            (name, score) 
            for name, score in capabilities.items() 
            if score < 0.7
        ]
        
        # 按分数排序
        weak_capabilities.sort(key=lambda x: x[1])
        
        # 生成推荐
        recommendations = []
        for cap_name, score in weak_capabilities[:3]:  # 只推荐前3个
            # 找到对应的贡献类型
            contribution_types = [
                ct for ct, c in self.CONTRIBUTION_TO_CAPABILITY.items() 
                if c == cap_name
            ]
            
            recommendations.append({
                "capability": cap_name,
                "current_score": score,
                "target_score": 0.7,
                "gap": 0.7 - score,
                "contribution_types": contribution_types,
                "suggested_actions": self._get_suggested_actions(cap_name)
            })
        
        return recommendations
    
    def _get_suggested_actions(self, capability: str) -> List[str]:
        """获取提升建议"""
        
        suggestions = {
            "市场洞察": [
                "关注行业动态，分享市场信息",
                "发现销售机会并提交",
                "分析竞争对手，提供洞察报告"
            ],
            "销售能力": [
                "跟进销售线索",
                "维护客户关系",
                "完成销售目标"
            ],
            "采购优化": [
                "发现低价优质供应商",
                "比较市场价格",
                "优化采购成本"
            ],
            "开发能力": [
                "完成开发任务",
                "优化代码质量",
                "解决技术难题"
            ],
            "人才识别": [
                "推荐优秀人才",
                "参与面试评估",
                "建立人才库"
            ],
            "知识输出": [
                "编写技术文档",
                "分享经验心得",
                "录制教程视频"
            ]
        }
        
        return suggestions.get(capability, ["继续在此领域贡献力量"])
    
    def calculate_capability_score(
        self,
        capabilities: Dict[str, float]
    ) -> float:
        """
        计算综合能力分数
        
        用于排行榜等场景
        """
        if not capabilities:
            return 0.0
        
        # 加权平均（可以后续优化权重）
        return sum(capabilities.values()) / len(capabilities)


# 全局能力引擎
capability_engine = CapabilityEngine()
