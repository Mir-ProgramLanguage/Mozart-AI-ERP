"""
回报计算引擎

核心功能：
1. 计算贡献对应的回报
2. 管理回报类型
3. 发放回报
"""

from typing import Dict, List
from decimal import Decimal
from datetime import datetime
from app.models.actor import Actor
from app.models.reward import Reward, RewardType, RewardStatus


class RewardCalculator:
    """回报计算引擎"""
    
    # 回报杠杆系数
    LEVERAGE = {
        RewardType.CASH_BONUS: Decimal("0.10"),         # 现金：贡献值的10%
        RewardType.PROFIT_SHARING: Decimal("0.40"),     # 利润分红：贡献值的40%（4倍杠杆）
        RewardType.STOCK_OPTIONS: Decimal("1.00"),      # 期权：1:1转换
        RewardType.SKILL_POINTS: Decimal("0.001"),      # 技能点：每1000贡献值=1点
    }
    
    # 最低回报门槛
    MIN_THRESHOLDS = {
        RewardType.CASH_BONUS: Decimal("10"),           # 最低10元
        RewardType.PROFIT_SHARING: Decimal("100"),      # 最低100元
        RewardType.STOCK_OPTIONS: Decimal("1000"),      # 最低1000元
        RewardType.SKILL_POINTS: Decimal("1"),          # 最低1点
    }
    
    def calculate_rewards(
        self, 
        contribution_value: float,
        actor_preferences: Dict = None
    ) -> Dict[str, Decimal]:
        """
        计算回报
        
        Args:
            contribution_value: 贡献值
            actor_preferences: Actor的回报偏好
            
        Returns:
            各类型回报金额
        """
        value = Decimal(str(contribution_value))
        rewards = {}
        
        # 1. 现金奖励
        cash = value * self.LEVERAGE[RewardType.CASH_BONUS]
        if cash >= self.MIN_THRESHOLDS[RewardType.CASH_BONUS]:
            rewards[RewardType.CASH_BONUS] = cash
        
        # 2. 利润分红（更高杠杆）
        profit_sharing = value * self.LEVERAGE[RewardType.PROFIT_SHARING]
        if profit_sharing >= self.MIN_THRESHOLDS[RewardType.PROFIT_SHARING]:
            rewards[RewardType.PROFIT_SHARING] = profit_sharing
        
        # 3. 技能点
        skill_points = value * self.LEVERAGE[RewardType.SKILL_POINTS]
        if skill_points >= self.MIN_THRESHOLDS[RewardType.SKILL_POINTS]:
            rewards[RewardType.SKILL_POINTS] = skill_points
        
        # 4. 期权（达到门槛才有）
        if value >= self.MIN_THRESHOLDS[RewardType.STOCK_OPTIONS]:
            stock = value * self.LEVERAGE[RewardType.STOCK_OPTIONS]
            rewards[RewardType.STOCK_OPTIONS] = stock
        
        return rewards
    
    def recommend_reward_type(
        self, 
        rewards: Dict[str, Decimal],
        actor_profile: Dict = None
    ) -> str:
        """
        推荐回报类型
        
        Args:
            rewards: 可选回报
            actor_profile: Actor档案
            
        Returns:
            推荐的回报类型
        """
        if not rewards:
            return None
        
        # 默认推荐利润分红（最高杠杆）
        if RewardType.PROFIT_SHARING in rewards:
            return RewardType.PROFIT_SHARING
        
        # 其次推荐现金
        if RewardType.CASH_BONUS in rewards:
            return RewardType.CASH_BONUS
        
        # 最后技能点
        if RewardType.SKILL_POINTS in rewards:
            return RewardType.SKILL_POINTS
        
        return list(rewards.keys())[0]
    
    def calculate_total_value(self, rewards: Dict[str, Decimal]) -> Decimal:
        """
        计算总回报价值（用于展示）
        
        利润分红按4倍计算实际价值
        """
        total = Decimal("0")
        
        for reward_type, amount in rewards.items():
            if reward_type == RewardType.PROFIT_SHARING:
                # 利润分红的实际价值按4倍计算
                total += amount * Decimal("4")
            else:
                total += amount
        
        return total


class RewardDistributor:
    """回报发放器"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.calculator = RewardCalculator()
    
    async def distribute(
        self,
        actor_id: str,
        event_id: str,
        contribution_value: float,
        contribution_type: str
    ) -> List[Reward]:
        """
        发放回报
        
        Args:
            actor_id: Actor ID
            event_id: 事件ID
            contribution_value: 贡献值
            contribution_type: 贡献类型
            
        Returns:
            发放的回报列表
        """
        # 1. 计算回报
        rewards_dict = self.calculator.calculate_rewards(contribution_value)
        
        # 2. 创建回报记录
        rewards = []
        for reward_type, amount in rewards_dict.items():
            reward = Reward(
                actor_id=actor_id,
                event_id=event_id,
                reward_type=reward_type,
                amount=float(amount),
                status=RewardStatus.PENDING,
                contribution_type=contribution_type,
                created_at=datetime.now()
            )
            rewards.append(reward)
        
        # 3. 保存到数据库
        # TODO: 实际保存逻辑
        # for reward in rewards:
        #     self.db.add(reward)
        # await self.db.commit()
        
        return rewards
    
    async def redeem(
        self,
        actor_id: str,
        reward_ids: List[str],
        reward_type: str
    ) -> Dict:
        """
        兑现回报
        
        Args:
            actor_id: Actor ID
            reward_ids: 回报ID列表
            reward_type: 兑现类型
            
        Returns:
            兑现结果
        """
        # TODO: 实现兑现逻辑
        # 1. 查询可用回报
        # 2. 检查是否可兑现
        # 3. 更新状态
        # 4. 发放（调用支付系统等）
        
        return {
            "status": "success",
            "message": f"已兑现{len(reward_ids)}个回报",
            "total_amount": 0
        }


# 工具函数
def format_reward_message(rewards: Dict[str, Decimal], contribution_value: float) -> str:
    """
    格式化回报消息
    
    用于展示给Actor
    """
    if not rewards:
        return f"感谢您的贡献！贡献值：{contribution_value:.2f}"
    
    messages = [f"恭喜！您获得了 {contribution_value:.2f} 贡献值"]
    
    if RewardType.CASH_BONUS in rewards:
        messages.append(f"💰 现金奖励：{rewards[RewardType.CASH_BONUS]:.2f}元")
    
    if RewardType.PROFIT_SHARING in rewards:
        messages.append(f"📈 利润分红：{rewards[RewardType.PROFIT_SHARING]:.2f}元（价值4倍）")
    
    if RewardType.SKILL_POINTS in rewards:
        messages.append(f"⭐ 技能点：{rewards[RewardType.SKILL_POINTS]:.2f}")
    
    if RewardType.STOCK_OPTIONS in rewards:
        messages.append(f"🎯 期权激励：{rewards[RewardType.STOCK_OPTIONS]:.2f}股")
    
    return "\n".join(messages)
