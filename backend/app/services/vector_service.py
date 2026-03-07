"""
向量存储服务 - Vector Service

核心功能：
1. 文本向量化（Embedding）
2. 向量存储（pgvector）
3. 语义搜索
4. 相似度计算
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 向量维度
EMBEDDING_DIMENSION = 1536  # OpenAI text-embedding-3-small


class VectorService:
    """
    向量服务

    使用 OpenAI/DeepSeek Embedding API 进行文本向量化
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "text-embedding-3-small",
        dimension: int = EMBEDDING_DIMENSION
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.dimension = dimension
        self.client = None

        if HAS_OPENAI and self.api_key:
            # DeepSeek 暂不支持 Embedding，使用 OpenAI
            base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )

    # ========== 向量化 ==========

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        将文本转换为向量

        Args:
            text: 输入文本

        Returns:
            向量列表，如果失败返回 None
        """
        if not self.client:
            # 没有配置 API，返回模拟向量
            return self._mock_embedding(text)

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text[:8000],  # 限制长度
                dimensions=self.dimension
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            return self._mock_embedding(text)

    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        批量向量化

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not self.client:
            return [self._mock_embedding(t) for t in texts]

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[t[:8000] for t in texts],
                dimensions=self.dimension
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [self._mock_embedding(t) for t in texts]

    def _mock_embedding(self, text: str) -> List[float]:
        """
        生成模拟向量（用于开发测试）

        基于文本内容生成确定性向量
        """
        import hashlib

        # 使用文本哈希生成确定性向量
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # 扩展到目标维度
        vector = []
        for i in range(self.dimension):
            byte_idx = i % len(hash_bytes)
            vector.append((hash_bytes[byte_idx] - 128) / 128.0)

        return vector

    # ========== 相似度计算 ==========

    def cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        计算余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            相似度 [-1, 1]
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def find_similar(
        self,
        query_vec: List[float],
        candidates: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        找到最相似的候选项

        Args:
            query_vec: 查询向量
            candidates: 候选列表，每项需要包含 'vector' 字段
            top_k: 返回数量

        Returns:
            排序后的候选列表
        """
        scored = []
        for candidate in candidates:
            vec = candidate.get("vector") or candidate.get("embedding")
            if vec:
                score = self.cosine_similarity(query_vec, vec)
                scored.append({
                    **candidate,
                    "similarity": score
                })

        # 按相似度排序
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]


class VectorStore:
    """
    向量存储

    使用数据库存储向量，支持语义搜索
    """

    def __init__(self, db=None, vector_service: VectorService = None):
        self.db = db
        self.vector_service = vector_service or VectorService()

    # ========== 存储操作 ==========

    async def store_event(
        self,
        event_id: str,
        content: str,
        metadata: Dict = None
    ) -> bool:
        """
        存储事件向量

        Args:
            event_id: 事件ID
            content: 事件内容
            metadata: 元数据

        Returns:
            是否成功
        """
        if not self.db:
            return False

        # 生成向量
        vector = await self.vector_service.embed_text(content)
        if not vector:
            return False

        # 更新数据库
        from app.models.contribution import Event
        from uuid import UUID

        try:
            event = self.db.query(Event).filter(
                Event.id == UUID(event_id)
            ).first()

            if event:
                # 存储向量（使用 JSON 格式）
                event.ai_analysis = event.ai_analysis or {}
                event.ai_analysis["embedding"] = vector
                self.db.commit()
                return True
        except Exception as e:
            print(f"Store event error: {e}")

        return False

    async def store_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> int:
        """
        批量存储

        Args:
            items: [{id, content, metadata}, ...]

        Returns:
            成功数量
        """
        success_count = 0
        for item in items:
            if await self.store_event(
                event_id=item["id"],
                content=item["content"],
                metadata=item.get("metadata")
            ):
                success_count += 1
        return success_count

    # ========== 搜索操作 ==========

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Dict = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索

        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件

        Returns:
            搜索结果
        """
        if not self.db:
            return []

        # 生成查询向量
        query_vec = await self.vector_service.embed_text(query)
        if not query_vec:
            return []

        # 从数据库获取候选
        from app.models.contribution import Event

        query_obj = self.db.query(Event)
        if filters:
            if filters.get("actor_id"):
                query_obj = query_obj.filter(Event.actor_id == filters["actor_id"])
            if filters.get("contribution_type"):
                query_obj = query_obj.filter(Event.contribution_type == filters["contribution_type"])

        events = query_obj.limit(100).all()

        # 计算相似度
        candidates = []
        for event in events:
            embedding = None
            if event.ai_analysis:
                embedding = event.ai_analysis.get("embedding")

            if embedding:
                candidates.append({
                    "id": str(event.id),
                    "content": event.content,
                    "vector": embedding,
                    "contribution_type": event.contribution_type,
                    "contribution_value": float(event.contribution_value) if event.contribution_value else 0,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                })

        # 找最相似的
        results = self.vector_service.find_similar(query_vec, candidates, top_k)

        # 移除向量字段
        for r in results:
            r.pop("vector", None)

        return results

    async def search_similar_events(
        self,
        event_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        查找相似事件

        Args:
            event_id: 参考事件ID
            top_k: 返回数量

        Returns:
            相似事件列表
        """
        if not self.db:
            return []

        from app.models.contribution import Event
        from uuid import UUID

        # 获取参考事件
        ref_event = self.db.query(Event).filter(
            Event.id == UUID(event_id)
        ).first()

        if not ref_event or not ref_event.ai_analysis:
            return []

        ref_vector = ref_event.ai_analysis.get("embedding")
        if not ref_vector:
            return []

        # 获取其他事件
        events = self.db.query(Event).filter(
            Event.id != UUID(event_id)
        ).limit(50).all()

        candidates = []
        for event in events:
            embedding = None
            if event.ai_analysis:
                embedding = event.ai_analysis.get("embedding")

            if embedding:
                candidates.append({
                    "id": str(event.id),
                    "content": event.content,
                    "vector": embedding,
                    "contribution_type": event.contribution_type
                })

        return self.vector_service.find_similar(ref_vector, candidates, top_k)


# 单例实例
_vector_service: Optional[VectorService] = None
_vector_store: Optional[VectorStore] = None


def get_vector_service() -> VectorService:
    """获取向量服务实例"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service


def get_vector_store(db=None) -> VectorStore:
    """获取向量存储实例"""
    global _vector_store
    if _vector_store is None or db:
        _vector_store = VectorStore(db)
    return _vector_store
