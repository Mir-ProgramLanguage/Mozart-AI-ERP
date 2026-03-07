"""
Actor 服务 - 能力个体管理

核心功能：
1. Actor 创建和管理
2. 能力成长算法
3. 信任分数计算
4. 任务匹配
"""
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.contribution import Actor, ActorType, Event, Task
from app.services.contribution_evaluator import ContributionEvaluator


class ActorService:
    """Actor 管理服务"""

    # 能力成长系数
    CAPABILITY_GROWTH_RATE = 0.01  # 每次贡献的基础成长率
    CAPABILITY_MAX = 1.0  # 能力上限
    CAPABILITY_MIN = 0.0  # 能力下限

    # 信任分数参数
    TRUST_BASE = 0.5  # 初始信任分数
    TRUST_INCREMENT = 0.02  # 每次成功贡献增加
    TRUST_DECREMENT = 0.05  # 每次失败减少
    TRUST_MAX = 1.0
    TRUST_MIN = 0.1

    def __init__(self, db: Session):
        self.db = db

    # ========== Actor CRUD ==========

    def create_actor(
        self,
        display_name: str,
        actor_type: str = ActorType.HUMAN,
        user_id: Optional[int] = None,
        capabilities: Optional[Dict[str, float]] = None,
        ai_config: Optional[Dict] = None
    ) -> Actor:
        """
        创建 Actor

        Args:
            display_name: 显示名称（代号）
            actor_type: 类型 (human/ai_agent/external)
            user_id: 关联用户ID（真实员工）
            capabilities: 初始能力
            ai_config: AI配置（虚拟员工）
        """
        actor = Actor(
            display_name=display_name,
            actor_type=actor_type,
            user_id=user_id,
            capabilities=capabilities or {},
            ai_config=ai_config or {},
            trust_score=self.TRUST_BASE
        )
        self.db.add(actor)
        self.db.commit()
        self.db.refresh(actor)
        return actor

    def get_actor(self, actor_id: UUID) -> Optional[Actor]:
        """获取 Actor"""
        return self.db.query(Actor).filter(Actor.id == actor_id).first()

    def get_actor_by_name(self, display_name: str) -> Optional[Actor]:
        """通过名称获取 Actor"""
        return self.db.query(Actor).filter(Actor.display_name == display_name).first()

    def list_actors(
        self,
        actor_type: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100
    ) -> List[Actor]:
        """列出 Actors"""
        query = self.db.query(Actor)
        if actor_type:
            query = query.filter(Actor.actor_type == actor_type)
        if is_active:
            query = query.filter(Actor.availability > 0)
        return query.limit(limit).all()

    # ========== 能力成长 ==========

    def grow_capability(
        self,
        actor: Actor,
        capability_name: str,
        contribution_value: float,
        reason: str = ""
    ) -> float:
        """
        能力成长算法

        成长公式：
        delta = base_rate * (1 + contribution_value / 10000) * (1 - current_level)
        
        解释：
        - 贡献价值越高，成长越快
        - 当前能力越高，成长越慢（边际效应递减）

        Args:
            actor: Actor 对象
            capability_name: 能力名称
            contribution_value: 贡献价值
            reason: 成长原因

        Returns:
            新的能力值
        """
        current = actor.capabilities.get(capability_name, 0.0) if actor.capabilities else 0.0

        # 成长计算
        growth_factor = 1 + contribution_value / 10000  # 贡献价值加成
        diminishing_returns = 1 - current  # 边际递减
        delta = self.CAPABILITY_GROWTH_RATE * growth_factor * diminishing_returns

        new_value = min(self.CAPABILITY_MAX, current + delta)

        # 更新能力
        if not actor.capabilities:
            actor.capabilities = {}
        actor.capabilities[capability_name] = new_value

        # 记录历史
        if not actor.capability_history:
            actor.capability_history = []
        actor.capability_history.append({
            "date": datetime.utcnow().isoformat(),
            "capability": capability_name,
            "old": current,
            "new": new_value,
            "delta": delta,
            "reason": reason
        })

        self.db.commit()
        return new_value

    def batch_grow_capabilities(
        self,
        actor: Actor,
        capabilities: Dict[str, float],
        reason: str = ""
    ) -> Dict[str, float]:
        """
        批量更新能力

        Args:
            actor: Actor 对象
            capabilities: {能力名: 贡献价值}
            reason: 原因

        Returns:
            更新后的能力字典
        """
        results = {}
        for cap_name, value in capabilities.items():
            results[cap_name] = self.grow_capability(actor, cap_name, value, reason)
        return results

    def get_capability_rank(self, actor: Actor, capability_name: str) -> int:
        """获取某项能力的排名"""
        actors = self.db.query(Actor).filter(
            Actor.capabilities[capability_name].isnot(None)
        ).all()

        sorted_actors = sorted(
            actors,
            key=lambda a: a.capabilities.get(capability_name, 0),
            reverse=True
        )

        for i, a in enumerate(sorted_actors):
            if str(a.id) == str(actor.id):
                return i + 1
        return -1

    # ========== 信任分数 ==========

    def update_trust_score(
        self,
        actor: Actor,
        success: bool,
        magnitude: float = 1.0
    ) -> float:
        """
        更新信任分数

        Args:
            actor: Actor 对象
            success: 是否成功
            magnitude: 影响系数

        Returns:
            新的信任分数
        """
        current = float(actor.trust_score) if actor.trust_score else self.TRUST_BASE

        if success:
            delta = self.TRUST_INCREMENT * magnitude
            new_score = min(self.TRUST_MAX, current + delta)
        else:
            delta = self.TRUST_DECREMENT * magnitude
            new_score = max(self.TRUST_MIN, current - delta)

        actor.trust_score = new_score
        self.db.commit()
        return new_score

    def calculate_reputation(self, actor: Actor) -> float:
        """
        计算声誉分数

        基于多个因素：
        - 总贡献值
        - 任务完成率
        - 信任分数
        """
        total_contributions = float(actor.total_contributions) if actor.total_contributions else 0
        contribution_factor = min(1.0, total_contributions / 100000)  # 10万贡献值满分

        # 任务完成率
        completed = actor.contribution_count or 0
        task_factor = min(1.0, completed / 100)  # 100次贡献满分

        trust = float(actor.trust_score) if actor.trust_score else 0.5

        reputation = (contribution_factor * 0.3 + task_factor * 0.3 + trust * 0.4)
        actor.reputation_score = reputation
        self.db.commit()
        return reputation

    # ========== 任务匹配 ==========

    def find_best_match(
        self,
        required_capabilities: Dict[str, float],
        exclude_ids: List[UUID] = None,
        min_trust: float = 0.3
    ) -> Optional[Actor]:
        """
        找到最匹配的 Actor

        基于能力匹配和信任分数

        Args:
            required_capabilities: 所需能力 {能力名: 最低要求}
            exclude_ids: 排除的 Actor ID
            min_trust: 最低信任分数

        Returns:
            最匹配的 Actor
        """
        query = self.db.query(Actor).filter(
            Actor.trust_score >= min_trust,
            Actor.availability > 0
        )

        if exclude_ids:
            query = query.filter(~Actor.id.in_(exclude_ids))

        actors = query.all()
        if not actors:
            return None

        best_actor = None
        best_score = -1

        for actor in actors:
            score = self._calculate_match_score(actor, required_capabilities)
            if score > best_score:
                best_score = score
                best_actor = actor

        return best_actor

    def _calculate_match_score(
        self,
        actor: Actor,
        required_capabilities: Dict[str, float]
    ) -> float:
        """
        计算匹配分数

        考虑因素：
        1. 能力匹配度
        2. 信任分数
        3. 当前负载
        """
        if not actor.capabilities:
            return 0

        # 能力匹配
        capability_scores = []
        for cap_name, min_level in required_capabilities.items():
            actor_level = actor.capabilities.get(cap_name, 0)
            if actor_level < min_level:
                return 0  # 不满足最低要求
            # 超出要求的程度
            excess = (actor_level - min_level) / (1 - min_level) if min_level < 1 else 0
            capability_scores.append(excess)

        capability_score = sum(capability_scores) / len(capability_scores) if capability_scores else 0

        # 信任分数
        trust = float(actor.trust_score) if actor.trust_score else 0.5

        # 可用性
        availability = float(actor.availability) if actor.availability else 1.0

        # 综合分数
        total_score = (
            capability_score * 0.5 +
            trust * 0.3 +
            availability * 0.2
        )

        return total_score

    # ========== 统计 ==========

    def update_statistics(self, actor: Actor) -> None:
        """更新统计信息"""
        # 更新贡献统计
        events = self.db.query(Event).filter(
            Event.actor_id == actor.id,
            Event.contribution_status == "verified"
        ).all()

        total = sum(float(e.contribution_value or 0) for e in events)
        actor.total_contributions = total
        actor.contribution_count = len(events)

        # 分类统计
        by_type = {}
        for event in events:
            ctype = event.contribution_type or "other"
            by_type[ctype] = by_type.get(ctype, 0) + float(event.contribution_value or 0)
        actor.contributions_by_type = by_type

        # 更新回报统计
        from app.models.contribution import Reward
        rewards = self.db.query(Reward).filter(Reward.actor_id == actor.id).all()
        actor.total_rewards = sum(float(r.amount or 0) for r in rewards)
        actor.available_rewards = sum(
            float(r.amount or 0) for r in rewards if r.status == "pending"
        )

        # 更新活跃时间
        actor.last_active = datetime.utcnow()

        self.db.commit()

    def get_leaderboard(
        self,
        by: str = "total_contributions",
        limit: int = 10
    ) -> List[Dict]:
        """
        获取排行榜

        Args:
            by: 排序字段 (total_contributions/trust_score/reputation_score)
            limit: 返回数量
        """
        actors = self.db.query(Actor).order_by(
            getattr(Actor, by).desc()
        ).limit(limit).all()

        return [
            {
                "rank": i + 1,
                "id": str(a.id),
                "display_name": a.display_name,
                "actor_type": a.actor_type,
                "value": float(getattr(a, by) or 0),
                "capabilities": a.capabilities
            }
            for i, a in enumerate(actors)
        ]
