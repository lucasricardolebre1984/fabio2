"""
Hybrid memory service for VIVA:
- short memory: current chat session snapshot (PostgreSQL chat tables)
- medium memory: rolling context in Redis
- long memory: semantic vectors in pgvector (PostgreSQL)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import json
import re

from redis import asyncio as redis_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.openai_service import openai_service


class VivaMemoryService:
    def __init__(self) -> None:
        self.redis_url = settings.REDIS_URL
        self._redis: Optional[redis_asyncio.Redis] = None
        self.embedding_dim = 1536
        self.medium_ttl_seconds = 60 * 60 * 24 * 7
        self.medium_max_items = 40
        self.vector_enabled = False
        self._storage_checked = False
        self._stopwords = {
            "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "um", "uma",
            "para", "com", "que", "por", "se", "ao", "aos", "as", "o", "os", "eu", "voce",
            "viva", "amanha", "hoje", "ontem",
        }

    async def _get_redis(self) -> Optional[redis_asyncio.Redis]:
        if self._redis is not None:
            return self._redis
        try:
            client = redis_asyncio.from_url(self.redis_url, decode_responses=True)
            await client.ping()
            self._redis = client
            return client
        except Exception:
            return None

    @staticmethod
    def _normalize_mode(modo: Optional[str]) -> Optional[str]:
        if not modo:
            return None
        normalized = str(modo).strip().upper()
        if normalized in {"FC", "REZETA", "LOGO"}:
            return normalized
        return None

    @staticmethod
    def _clean_text(value: str) -> str:
        collapsed = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
        return collapsed.strip()

    def _tokenize(self, text_value: str) -> List[str]:
        clean = self._clean_text(text_value).lower()
        if not clean:
            return []
        tokens = re.findall(r"[a-z0-9]{2,}", clean)
        filtered: List[str] = []
        for token in tokens:
            if token in self._stopwords:
                continue
            if len(token) < 3 and not token.isdigit():
                continue
            filtered.append(token)
        return filtered[:24]

    def _lexical_overlap_score(self, query_tokens: List[str], content: str) -> float:
        if not query_tokens:
            return 0.0
        content_tokens = set(self._tokenize(content))
        if not content_tokens:
            return 0.0
        overlap = sum(1 for token in query_tokens if token in content_tokens)
        return float(overlap) / float(max(1, len(set(query_tokens))))

    @staticmethod
    def _recency_score(created_at: Any) -> float:
        if not isinstance(created_at, datetime):
            return 0.0
        dt = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
        age_seconds = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())
        age_hours = age_seconds / 3600.0
        # Decaimento suave: ainda valoriza contexto dos ultimos dias sem apagar historico.
        return 1.0 / (1.0 + age_hours / 72.0)

    @staticmethod
    def _created_at_rank(created_at: Any) -> float:
        if not isinstance(created_at, datetime):
            return 0.0
        dt = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
        try:
            return float(dt.timestamp())
        except Exception:
            return 0.0

    @staticmethod
    def _vector_literal(embedding: List[float]) -> str:
        return "[" + ",".join(f"{float(item):.10f}" for item in embedding) + "]"

    def _coerce_embedding_dim(self, embedding: Optional[List[float]]) -> Optional[List[float]]:
        if not embedding:
            return None
        vector = [float(item) for item in embedding if item is not None]
        if not vector:
            return None

        target = int(self.embedding_dim)
        if len(vector) > target:
            return vector[:target]
        if len(vector) < target:
            return vector + [0.0] * (target - len(vector))
        return vector

    async def ensure_storage(self, db: AsyncSession) -> Dict[str, bool]:
        if self._storage_checked and self.vector_enabled:
            redis_ok = bool(await self._get_redis())
            return {"vector": self.vector_enabled, "redis": redis_ok}

        vector_ok = False
        try:
            async with db.begin_nested():
                await db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await db.execute(
                    text(
                        f"""
                        CREATE TABLE IF NOT EXISTS viva_memory_vectors (
                            id UUID PRIMARY KEY,
                            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            session_id UUID NOT NULL,
                            tipo VARCHAR(16) NOT NULL,
                            modo VARCHAR(32),
                            conteudo TEXT NOT NULL,
                            meta_json JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                            embedding VECTOR({self.embedding_dim}) NOT NULL,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                )
                await db.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS idx_viva_memory_user_created
                        ON viva_memory_vectors(user_id, created_at DESC)
                        """
                    )
                )
                await db.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS idx_viva_memory_session_created
                        ON viva_memory_vectors(session_id, created_at DESC)
                        """
                    )
                )
                await db.execute(
                    text(
                        """
                        CREATE INDEX IF NOT EXISTS idx_viva_memory_embedding_ivfflat
                        ON viva_memory_vectors USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100)
                        """
                    )
                )
            vector_ok = True
        except Exception:
            vector_ok = False

        self.vector_enabled = vector_ok
        self._storage_checked = vector_ok
        redis_ok = bool(await self._get_redis())
        return {"vector": vector_ok, "redis": redis_ok}

    async def append_medium_memory(
        self,
        session_id: UUID,
        tipo: str,
        conteudo: str,
        modo: Optional[str],
    ) -> bool:
        redis_client = await self._get_redis()
        if not redis_client:
            return False

        clean = self._clean_text(conteudo)
        if not clean:
            return False

        payload = {
            "tipo": tipo,
            "conteudo": clean,
            "modo": self._normalize_mode(modo),
            "created_at": datetime.utcnow().isoformat(),
        }
        key = f"viva:memory:session:{session_id}:medium"
        try:
            await redis_client.lpush(key, json.dumps(payload, ensure_ascii=False))
            await redis_client.ltrim(key, 0, self.medium_max_items - 1)
            await redis_client.expire(key, self.medium_ttl_seconds)
            return True
        except Exception:
            return False

    async def get_medium_memory(self, session_id: UUID, limit: int = 8) -> List[Dict[str, Any]]:
        redis_client = await self._get_redis()
        if not redis_client:
            return []

        safe_limit = max(1, min(limit, 30))
        key = f"viva:memory:session:{session_id}:medium"
        try:
            raw = await redis_client.lrange(key, 0, safe_limit - 1)
        except Exception:
            return []

        items: List[Dict[str, Any]] = []
        for entry in raw:
            try:
                parsed = json.loads(entry)
                if isinstance(parsed, dict):
                    items.append(parsed)
            except Exception:
                continue
        items.reverse()
        return items

    async def append_long_memory(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        tipo: str,
        conteudo: str,
        modo: Optional[str],
        meta: Optional[Dict[str, Any]] = None,
    ) -> bool:
        await self.ensure_storage(db)
        if not self.vector_enabled:
            return False

        clean = self._clean_text(conteudo)
        if len(clean) < 12:
            return False

        embedding = self._coerce_embedding_dim(await openai_service.embed_text(clean))
        if not embedding:
            return False

        normalized_mode = self._normalize_mode(modo)
        try:
            async with db.begin_nested():
                await db.execute(
                    text(
                        """
                        INSERT INTO viva_memory_vectors (
                            id, user_id, session_id, tipo, modo, conteudo, meta_json, embedding, created_at
                        )
                        VALUES (
                            :id, :user_id, :session_id, :tipo, :modo, :conteudo,
                            CAST(:meta_json AS JSONB), CAST(:embedding AS vector), NOW()
                        )
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "user_id": str(user_id),
                        "session_id": str(session_id),
                        "tipo": tipo,
                        "modo": normalized_mode,
                        "conteudo": clean,
                        "meta_json": json.dumps(meta or {}, ensure_ascii=False),
                        "embedding": self._vector_literal(embedding),
                    },
                )
            return True
        except Exception:
            return False

    async def append_memory(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        tipo: str,
        conteudo: str,
        modo: Optional[str],
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, bool]:
        medium_ok = await self.append_medium_memory(session_id=session_id, tipo=tipo, conteudo=conteudo, modo=modo)
        long_ok = await self.append_long_memory(
            db=db,
            user_id=user_id,
            session_id=session_id,
            tipo=tipo,
            conteudo=conteudo,
            modo=modo,
            meta=meta,
        )
        return {"medium": medium_ok, "long": long_ok}

    async def search_long_memory(
        self,
        db: AsyncSession,
        user_id: UUID,
        query: str,
        modo: Optional[str],
        limit: int = 6,
    ) -> List[Dict[str, Any]]:
        await self.ensure_storage(db)
        clean_query = self._clean_text(query)
        if not clean_query:
            return []

        safe_limit = max(1, min(limit, 20))
        normalized_mode = self._normalize_mode(modo)
        where = "WHERE user_id = :user_id"
        params: Dict[str, Any] = {
            "user_id": str(user_id),
        }
        if normalized_mode:
            where += " AND modo = :modo"
            params["modo"] = normalized_mode

        query_tokens = self._tokenize(clean_query)
        vector_rows: List[Any] = []
        keyword_rows: List[Any] = []

        if self.vector_enabled:
            embedding = self._coerce_embedding_dim(await openai_service.embed_text(clean_query))
            if embedding:
                vector_params = {
                    **params,
                    "query_embedding": self._vector_literal(embedding),
                    "vector_limit": max(24, min(120, safe_limit * 8)),
                }
                try:
                    async with db.begin_nested():
                        result = await db.execute(
                            text(
                                f"""
                                SELECT id, tipo, modo, conteudo, created_at,
                                       1 - (embedding <=> CAST(:query_embedding AS vector)) AS score
                                FROM viva_memory_vectors
                                {where}
                                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                                LIMIT :vector_limit
                                """
                            ),
                            vector_params,
                        )
                        vector_rows = result.fetchall()
                except Exception:
                    vector_rows = []

        if query_tokens:
            keyword_params: Dict[str, Any] = {
                **params,
                "keyword_limit": max(20, min(120, safe_limit * 8)),
            }
            clauses: List[str] = []
            for idx, token in enumerate(query_tokens[:6]):
                key = f"kw_{idx}"
                keyword_params[key] = f"%{token}%"
                clauses.append(f"conteudo ILIKE :{key}")
            if clauses:
                keyword_where = f"{where} AND ({' OR '.join(clauses)})"
                try:
                    async with db.begin_nested():
                        result = await db.execute(
                            text(
                                f"""
                                SELECT id, tipo, modo, conteudo, created_at,
                                       0.0 AS score
                                FROM viva_memory_vectors
                                {keyword_where}
                                ORDER BY created_at DESC
                                LIMIT :keyword_limit
                                """
                            ),
                            keyword_params,
                        )
                        keyword_rows = result.fetchall()
                except Exception:
                    keyword_rows = []

        if not vector_rows and not keyword_rows:
            return []

        candidates: Dict[str, Dict[str, Any]] = {}
        for row in vector_rows:
            key = str(row.id)
            candidates[key] = {
                "id": row.id,
                "tipo": row.tipo,
                "modo": row.modo,
                "conteudo": row.conteudo,
                "created_at": row.created_at,
                "vector_score": float(row.score or 0.0),
            }

        for row in keyword_rows:
            key = str(row.id)
            existing = candidates.get(key)
            if existing:
                continue
            candidates[key] = {
                "id": row.id,
                "tipo": row.tipo,
                "modo": row.modo,
                "conteudo": row.conteudo,
                "created_at": row.created_at,
                "vector_score": 0.0,
            }

        has_vector_signal = bool(vector_rows)
        rescored: List[Dict[str, Any]] = []
        for item in candidates.values():
            lexical_score = self._lexical_overlap_score(query_tokens, str(item.get("conteudo") or ""))
            recency_score = self._recency_score(item.get("created_at"))
            vector_score = float(item.get("vector_score") or 0.0)
            if has_vector_signal:
                final_score = (vector_score * 0.72) + (lexical_score * 0.22) + (recency_score * 0.06)
            else:
                final_score = (lexical_score * 0.85) + (recency_score * 0.15)
            rescored.append(
                {
                    "id": item["id"],
                    "tipo": item["tipo"],
                    "modo": item["modo"],
                    "conteudo": item["conteudo"],
                    "created_at": item["created_at"],
                    "score": float(final_score),
                    "vector_score": float(vector_score),
                    "lexical_score": float(lexical_score),
                    "recency_score": float(recency_score),
                }
            )

        rescored.sort(
            key=lambda item: (
                float(item.get("score") or 0.0),
                float(item.get("vector_score") or 0.0),
                self._created_at_rank(item.get("created_at")),
            ),
            reverse=True,
        )
        return rescored[:safe_limit]

    async def build_chat_memory_context(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        query: str,
        modo: Optional[str],
    ) -> str:
        medium = await self.get_medium_memory(session_id=session_id, limit=8)
        long_hits = await self.search_long_memory(db=db, user_id=user_id, query=query, modo=modo, limit=6)

        lines: List[str] = []
        if medium:
            lines.append("Memoria media recente da sessao:")
            for item in medium[-6:]:
                tipo = str(item.get("tipo") or "msg")
                content = self._clean_text(str(item.get("conteudo") or ""))
                if content:
                    lines.append(f"- ({tipo}) {content[:220]}")

        if long_hits:
            lines.append("Memoria longa recuperada por similaridade:")
            for hit in long_hits:
                content = self._clean_text(str(hit.get("conteudo") or ""))
                if content:
                    lines.append(f"- {content[:260]}")

        unique_lines: List[str] = []
        seen: set[str] = set()
        for line in lines:
            key = re.sub(r"\s+", " ", line.strip().lower())
            if not key or key in seen:
                continue
            seen.add(key)
            unique_lines.append(line)

        if not unique_lines:
            return ""
        return "\n".join(unique_lines[:14])

    async def reindex_from_chat_messages(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 400,
        session_id: Optional[UUID] = None,
    ) -> Dict[str, int]:
        await self.ensure_storage(db)
        if not self.vector_enabled:
            return {"processed": 0, "indexed": 0}

        safe_limit = max(1, min(limit, 2000))
        where = "WHERE m.user_id = :user_id"
        params: Dict[str, Any] = {"user_id": str(user_id), "limit": safe_limit}
        if session_id:
            where += " AND m.session_id = :session_id"
            params["session_id"] = str(session_id)

        result = await db.execute(
            text(
                f"""
                SELECT m.session_id, m.tipo, m.conteudo, m.modo, m.created_at
                FROM viva_chat_messages m
                {where}
                ORDER BY m.created_at DESC
                LIMIT :limit
                """
            ),
            params,
        )

        processed = 0
        indexed = 0
        for row in result.fetchall():
            processed += 1
            ok = await self.append_long_memory(
                db=db,
                user_id=user_id,
                session_id=row.session_id,
                tipo=row.tipo,
                conteudo=row.conteudo,
                modo=row.modo,
                meta={"source": "chat_reindex", "created_at": str(row.created_at)},
            )
            if ok:
                indexed += 1
        return {"processed": processed, "indexed": indexed}

    async def memory_status(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_id: Optional[UUID],
    ) -> Dict[str, Any]:
        availability = await self.ensure_storage(db)
        total_vectors = 0
        if availability["vector"]:
            try:
                async with db.begin_nested():
                    count = await db.execute(
                        text("SELECT COUNT(*) FROM viva_memory_vectors WHERE user_id = :user_id"),
                        {"user_id": str(user_id)},
                    )
                total_vectors = int(count.scalar() or 0)
            except Exception:
                total_vectors = 0

        medium_items = 0
        if session_id and availability["redis"]:
            medium_items = len(await self.get_medium_memory(session_id=session_id, limit=50))

        return {
            "vector_enabled": availability["vector"],
            "redis_enabled": availability["redis"],
            "total_vectors": total_vectors,
            "medium_items": medium_items,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "embedding_runtime": openai_service.get_embedding_runtime_status(),
        }


viva_memory_service = VivaMemoryService()
