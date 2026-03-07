"""
智能分配算法 - Smart Assigner

核心功能：
1. 基于能力匹配分配任务
2. 负载均衡
3. 紧急任务快速通道
4. 历史表现考量
"""
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID
import math


@dataclass
class AssignmentScore:
    """分配评分"""
    actor_id: UUID
    score: float
    capability_match: float
    availability: float
    workload: float
    performance: float
    reasons: List[str]


class SmartAssigner:
    """
    智能任务分配器

    综合考虑能力、负载、表现等因素进行最优分配
    """

    # 权重配置
    WEIGHTS = {
        "capability": 0.35,   # 能力匹配权重
        "availability": 0.20, # 可用性权重
        "workload": 0.25,     # 负载权重（负向，负载越高分数越低）
        "performance": 0.20,  # 历史表现权重
    }

    # 负载阈值
    MAX_CONCURRENT_TASKS = 5  # 最大并发任务数
    MAX_DAILY_HOURS = 8       # 每日最大工作时长

    def __init__(self, db=None):
        self.db = db

    # ========== 主分配方法 ==========

    def find_best_assignee(
        self,
        required_capabilities: Dict[str, float],
        exclude_ids: List[UUID] = None,
        min_trust: float = 0.3,
        urgency: int = 0
    ) -> Optional[AssignmentScore]:
        """
        找到最佳分配对象

        Args:
            required_capabilities: 所需能力 {能力名: 最低要求}
            exclude_ids: 排除的 Actor ID
            min_trust: 最低信任分数
            urgency: 紧急程度 0-10

        Returns:
            AssignmentScore: 最佳分配评分
        """
        if not self.db:
            return None

        from app.services.actor_service import ActorService
        from app.models.contribution import Actor

        actor_service = ActorService(self.db)

        # 获取候选 Actors
        candidates = self._get_candidates(
            actor_service,
            min_trust=min_trust,
            exclude_ids=exclude_ids
        )

        if not candidates:
            return None

        # 计算每个候选的分数
        scores = []
        for actor in candidates:
            score = self._calculate_assignment_score(
                actor,
                required_capabilities,
                urgency
            )
            scores.append(score)

        # 排序并返回最佳
        scores.sort(key=lambda x: x.score, reverse=True)
        return scores[0] if scores else None

    def assign_to_multiple(
        self,
        required_capabilities: Dict[str, float],
        count: int = 2,
        exclude_ids: List[UUID] = None
    ) -> List[AssignmentScore]:
        """
        分配给多个人（协同任务）

        Args:
            required_capabilities: 所需能力
            count: 需要的人数
            exclude_ids: 排除的 Actor ID

        Returns:
            排序后的分配评分列表
        """
        if not self.db:
            return []

        from app.services.actor_service import ActorService

        actor_service = ActorService(self.db)
        candidates = self._get_candidates(actor_service, exclude_ids=exclude_ids)

        scores = []
        for actor in candidates:
            score = self._calculate_assignment_score(actor, required_capabilities)
            scores.append(score)

        scores.sort(key=lambda x: x.score, reverse=True)
        return scores[:count]

    # ========== 评分计算 ==========

    def _calculate_assignment_score(
        self,
        actor: "Actor",
        required_capabilities: Dict[str, float],
        urgency: int = 0
    ) -> AssignmentScore:
        """
        计算分配评分

        综合评分 = 能力匹配 × 0.35 + 可用性 × 0.20 + 负载因子 × 0.25 + 历史表现 × 0.20
        """
        reasons = []

        # 1. 能力匹配度
        capability_match = self._calculate_capability_match(
            actor.capabilities or {},
            required_capabilities
        )
        if capability_match < 0.5:
            reasons.append(f"能力匹配度较低 ({capability_match:.2f})")
        else:
            reasons.append(f"能力匹配良好 ({capability_match:.2f})")

        # 2. 可用性
        availability = float(actor.availability or 1.0)
        reasons.append(f"可用性 {availability:.0%}")

        # 3. 负载因子
        workload = self._calculate_workload_factor(actor)
        if workload < 0.5:
            reasons.append(f"负载较重 ({workload:.2f})")
        else:
            reasons.append(f"负载适中 ({workload:.2f})")

        # 4. 历史表现
        performance = self._calculate_performance_factor(actor)
        reasons.append(f"历史表现 {performance:.2f}")

        # 综合评分
        total_score = (
            capability_match * self.WEIGHTS["capability"] +
            availability * self.WEIGHTS["availability"] +
            workload * self.WEIGHTS["workload"] +
            performance * self.WEIGHTS["performance"]
        )

        # 紧急任务加成
        if urgency >= 7:
            # 紧急任务更看重可用性和负载
            total_score = (
                capability_match * 0.30 +
                availability * 0.30 +
                workload * 0.25 +
                performance * 0.15
            )
            reasons.append("紧急任务加成")

        return AssignmentScore(
            actor_id=actor.id,
            score=total_score,
            capability_match=capability_match,
            availability=availability,
            workload=workload,
            performance=performance,
            reasons=reasons
        )

    def _calculate_capability_match(
        self,
        actor_capabilities: Dict[str, float],
        required_capabilities: Dict[str, float]
    ) -> float:
        """
        计算能力匹配度

        如果 Actor 能力低于要求，则不匹配
        如果 Actor 能力高于要求，则按超出比例加分
        """
        if not required_capabilities:
            return 1.0  # 无要求，默认匹配

        if not actor_capabilities:
            return 0.0  # 没有能力，不匹配

        scores = []
        for cap_name, min_level in required_capabilities.items():
            actor_level = actor_capabilities.get(cap_name, 0.0)

            # 不满足最低要求
            if actor_level < min_level:
                return 0.0

            # 超出要求的程度 (0-1)
            # 例如: 要求0.6，有0.8，超出 0.2/(1-0.6) = 0.5
            excess = (actor_level - min_level) / (1 - min_level) if min_level < 1 else 0
            scores.append(0.6 + excess * 0.4)  # 基础分0.6，超额最多加0.4

        return sum(scores) / len(scores)

    def _calculate_workload_factor(self, actor: "Actor") -> float:
        """
        计算负载因子

        负载越高，因子越低（1 - 负载率）
        """
        current_tasks = actor.current_tasks or []
        task_count = len(current_tasks)

        # 负载率
        load_ratio = task_count / self.MAX_CONCURRENT_TASKS

        # 因子 = 1 - 负载率
        factor = 1 - min(1.0, load_ratio)

        return max(0.1, factor)  # 最低保留 0.1

    def _calculate_performance_factor(self, actor: "Actor") -> float:
        """
        计算历史表现因子

        基于信任分和声誉分
        """
        trust = float(actor.trust_score or 0.5)
        reputation = float(actor.reputation_score or 0.5)

        # 综合表现
        return (trust * 0.6 + reputation * 0.4)

    # ========== 候选获取 ==========

    def _get_candidates(
        self,
        actor_service: "ActorService",
        min_trust: float = 0.3,
        exclude_ids: List[UUID] = None
    ) -> List["Actor"]:
        """获取候选 Actors"""
        from app.models.contribution import Actor, ActorType

        query = self.db.query(Actor).filter(
            Actor.trust_score >= min_trust,
            Actor.availability > 0,
            Actor.actor_type != ActorType.EXTERNAL  # 排除外部合作者
        )

        if exclude_ids:
            query = query.filter(~Actor.id.in_(exclude_ids))

        return query.all()

    # ========== 负载均衡 ==========

    def balance_workload(self) -> Dict[str, List[UUID]]:
        """
        负载均衡

        找出过载和空闲的 Actor，为任务重分配提供建议

        Returns:
            {"overloaded": [...], "available": [...], "recommendations": [...]}
        """
        if not self.db:
            return {"overloaded": [], "available": [], "recommendations": []}

        from app.models.contribution import Actor

        actors = self.db.query(Actor).filter(
            Actor.availability > 0
        ).all()

        overloaded = []
        available = []

        for actor in actors:
            task_count = len(actor.current_tasks or [])
            if task_count >= self.MAX_CONCURRENT_TASKS:
                overloaded.append(actor.id)
            elif task_count <= 1:
                available.append(actor.id)

        return {
            "overloaded": overloaded,
            "available": available,
            "recommendation": f"建议从 {len(overloaded)} 个过载 Actor 转移任务到 {len(available)} 个空闲 Actor"
        }

    # ========== 快速通道 ==========

    def emergency_channel(
        self,
        required_capabilities: Dict[str, float]
    ) -> Optional[UUID]:
        """
        紧急任务快速通道

        只考虑可用性最高、负载最低的高信任 Actor
        """
        if not self.db:
            return None

        from app.models.contribution import Actor

        # 只选择高信任、低负载的 Actor
        actors = self.db.query(Actor).filter(
            Actor.trust_score >= 0.7,
            Actor.availability >= 0.8
        ).all()

        if not actors:
            return None

        # 找负载最低的
        best = min(actors, key=lambda a: len(a.current_tasks or []))

        # 确保有能力
        if required_capabilities:
            for cap_name, min_level in required_capabilities.items():
                if (best.capabilities or {}).get(cap_name, 0) < min_level:
                    return None

        return best.id
