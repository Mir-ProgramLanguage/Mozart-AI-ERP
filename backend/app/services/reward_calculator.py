"""
回报计算引擎 (Reward Calculator)

负责将贡献值转换为回报：
1. 根据贡献值计算各种回报类型
2. 应用回报杠杆（贡献值→回报）
3. 发放回报到Actor账户
4. 记录回报历史
"""

import json
from decimal import Decimal
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.contribution import (
    Actor, Event, Reward, RewardType, RewardStatus, ContributionStatus
)


class RewardCalculator:
    """
    回报计算引擎
    
    核心概念：
    - 贡献值是虚拟积分
    - 回报是真金白银
    - 通过杠杆将贡献值放大为回报
    
    回报杠杆：
    - 现金：贡献值的10%
    - 利润分红：贡献值的40%（4倍杠杆）
    - 期权：1:1转换
    - 技能点：每1000贡献值 = 1技能点
    """

    # 回报杠杆配置
    REWARD_LEVERAGE = {
        RewardType.CASH_BONUS: Decimal("0.1"),           # 现金：贡献值的10%
        RewardType.PROFIT_SHARING: Decimal("0.4"),       # 利润分红：贡献值的40%
        RewardType.STOCK_OPTIONS: Decimal("1.0"),        # 期权：1:1
    }

    # 最低门槛
    MIN_THRESHOLDS = {
        RewardType.CASH_BONUS: Decimal("10"),            # 最低10元
        RewardType.PROFIT_SHARING: Decimal("100"),       # 最低100元
        RewardType.STOCK_OPTIONS: Decimal("1000"),       # 最低1000元
    }

    # 技能点转换率
    SKILL_POINT_RATE = Decimal("1000")  # 每1000贡献值 = 1技能点

    def __init__(self, db: Session):
        self.db = db

    async def calculate(
        self,
        actor: Actor,
        contribution_value: Decimal,
        event_id: UUID,
        contribution_type: str = ""
    ) -> Dict[str, Any]:
        """
        计算回报
        
        根据贡献值自动计算各种类型的回报
        """
        rewards = {}

        # 1. 现金奖励
        cash = contribution_value * self.REWARD_LEVERAGE[RewardType.CASH_BONUS]
        if cash >= self.MIN_THRESHOLDS[RewardType.CASH_BONUS]:
            rewards[RewardType.CASH_BONUS] = cash

        # 2. 利润分红（更高杠杆）
        profit_sharing = contribution_value * self.REWARD_LEVERAGE[RewardType.PROFIT_SHARING]
        if profit_sharing >= self.MIN_THRESHOLDS[RewardType.PROFIT_SHARING]:
            rewards[RewardType.PROFIT_SHARING] = profit_sharing

        # 3. 技能点（提升能力）
        skill_points = contribution_value / self.SKILL_POINT_RATE
        if skill_points > 0:
            rewards[RewardType.SKILL_POINTS] = skill_points

        # 4. 期权（大额贡献）
        if contribution_value >= self.MIN_THRESHOLDS[RewardType.STOCK_OPTIONS]:
            rewards[RewardType.STOCK_OPTIONS] = contribution_value

        return {
            "contribution_value": float(contribution_value),
            "rewards": {k: float(v) for k, v in rewards.items()},
            "total_cash_value": float(cash + profit_sharing) if cash or profit_sharing else 0
        }

    async def distribute(
        self,
        actor_id: UUID,
        event_id: UUID,
        rewards: Dict[str, Decimal],
        contribution_type: str = ""
    ) -> List[Reward]:
        """
        发放回报
        
        创建回报记录并更新Actor余额
        """
        created_rewards = []

        for reward_type, amount in rewards.items():
            # 创建回报记录
            reward = Reward(
                actor_id=actor_id,
                event_id=event_id,
                reward_type=reward_type,
                amount=amount,
                contribution_type=contribution_type,
                status=RewardStatus.PENDING
            )
            self.db.add(reward)
            created_rewards.append(reward)

        # 更新Actor的回报余额
        actor = self.db.query(Actor).filter(Actor.id == actor_id).first()
        if actor:
            total_cash = sum(
                amount for rtype, amount in rewards.items()
                if rtype in [RewardType.CASH_BONUS, RewardType.PROFIT_SHARING]
            )
            actor.total_rewards = (actor.total_rewards or 0) + total_cash
            actor.available_rewards = (actor.available_rewards or 0) + total_cash

            # 更新回报历史
            history = actor.reward_history or []
            history.append({
                "type": "contribution_reward",
                "event_id": str(event_id),
                "rewards": {k: float(v) for k, v in rewards.items()},
                "timestamp": datetime.utcnow().isoformat()
            })
            actor.reward_history = history

        self.db.commit()

        return created_rewards

    async def process_event_reward(
        self,
        event: Event,
        actor: Actor
    ) -> Dict[str, Any]:
        """
        处理事件回报
        
        完整流程：计算回报 → 发放回报
        """
        if event.contribution_status != ContributionStatus.VERIFIED:
            return {
                "success": False,
                "message": "贡献尚未验证，无法发放回报"
            }

        contribution_value = event.actual_value or event.contribution_value
        if not contribution_value:
            return {
                "success": False,
                "message": "贡献价值为0，无法发放回报"
            }

        # 计算回报
        calculation = await self.calculate(
            actor=actor,
            contribution_value=Decimal(str(contribution_value)),
            event_id=event.id,
            contribution_type=event.contribution_type or ""
        )

        # 发放回报
        rewards = await self.distribute(
            actor_id=actor.id,
            event_id=event.id,
            rewards={k: Decimal(str(v)) for k, v in calculation["rewards"].items()},
            contribution_type=event.contribution_type or ""
        )

        return {
            "success": True,
            "event_id": str(event.id),
            "contribution_value": calculation["contribution_value"],
            "rewards_distributed": len(rewards),
            "rewards": calculation["rewards"],
            "message": f"已发放 {len(rewards)} 种回报"
        }

    async def claim_reward(
        self,
        reward_id: UUID,
        actor_id: UUID
    ) -> Dict[str, Any]:
        """
        兑现回报
        
        将待兑现回报转为已兑现
        """
        reward = self.db.query(Reward).filter(
            Reward.id == reward_id,
            Reward.actor_id == actor_id,
            Reward.status == RewardStatus.PENDING
        ).first()

        if not reward:
            return {
                "success": False,
                "message": "回报不存在或已兑现"
            }

        # 更新回报状态
        reward.status = RewardStatus.CLAIMED
        reward.claimed_at = datetime.utcnow()

        # 更新Actor余额（仅扣减现金类回报）
        actor = self.db.query(Actor).filter(Actor.id == actor_id).first()
        if actor and reward.reward_type in [RewardType.CASH_BONUS, RewardType.PROFIT_SHARING]:
            actor.available_rewards = max(
                (actor.available_rewards or 0) - reward.amount,
                Decimal("0")
            )

        self.db.commit()

        return {
            "success": True,
            "reward_id": str(reward.id),
            "reward_type": reward.reward_type,
            "amount": float(reward.amount),
            "claimed_at": reward.claimed_at.isoformat()
        }

    def get_actor_rewards(
        self,
        actor_id: UUID,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取Actor的回报列表
        """
        query = self.db.query(Reward).filter(Reward.actor_id == actor_id)
        
        if status:
            query = query.filter(Reward.status == status)
        
        rewards = query.order_by(Reward.created_at.desc()).all()
        return [r.to_dict() for r in rewards]

    def get_available_rewards(self, actor_id: UUID) -> Dict[str, Any]:
        """
        获取Actor可兑现的回报
        """
        rewards = self.db.query(Reward).filter(
            Reward.actor_id == actor_id,
            Reward.status == RewardStatus.PENDING
        ).all()

        # 按类型分组
        by_type = {}
        total = Decimal("0")
        
        for reward in rewards:
            if reward.reward_type not in by_type:
                by_type[reward.reward_type] = Decimal("0")
            by_type[reward.reward_type] += reward.amount
            total += reward.amount

        return {
            "total_available": float(total),
            "by_type": {k: float(v) for k, v in by_type.items()},
            "pending_count": len(rewards)
        }
