"""
Handoff orchestration for VIVA -> Viviane (WhatsApp reminders).
"""
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cofre_memory_service import cofre_memory_service
from app.services.whatsapp_service import WhatsAppService


class VivaHandoffService:
    async def ensure_table(self, db: AsyncSession) -> None:
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS viva_handoff_tasks (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    agenda_event_id UUID NULL,
                    cliente_nome VARCHAR(160),
                    cliente_numero VARCHAR(40) NOT NULL,
                    mensagem TEXT NOT NULL,
                    scheduled_for TIMESTAMPTZ NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    sent_at TIMESTAMPTZ,
                    last_error TEXT,
                    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_handoff_user_created
                ON viva_handoff_tasks(user_id, created_at DESC)
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_handoff_status_schedule
                ON viva_handoff_tasks(status, scheduled_for ASC)
                """
            )
        )

    async def schedule_task(
        self,
        db: AsyncSession,
        user_id: UUID,
        cliente_numero: str,
        mensagem: str,
        scheduled_for: datetime,
        cliente_nome: Optional[str] = None,
        agenda_event_id: Optional[UUID] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        await self.ensure_table(db)
        task_id = uuid4()
        payload = {
            "id": str(task_id),
            "user_id": str(user_id),
            "agenda_event_id": str(agenda_event_id) if agenda_event_id else None,
            "cliente_nome": cliente_nome,
            "cliente_numero": cliente_numero,
            "mensagem": mensagem,
            "scheduled_for": scheduled_for,
            "meta_json": json.dumps(meta or {}, ensure_ascii=False),
        }
        await db.execute(
            text(
                """
                INSERT INTO viva_handoff_tasks (
                    id, user_id, agenda_event_id, cliente_nome, cliente_numero,
                    mensagem, scheduled_for, status, attempts, meta_json, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :agenda_event_id, :cliente_nome, :cliente_numero,
                    :mensagem, :scheduled_for, 'pending', 0,
                    CAST(:meta_json AS JSONB), NOW(), NOW()
                )
                """
            ),
            payload,
        )
        await db.commit()
        cofre_memory_service.log_event(
            table_name="viva_handoff_tasks",
            action="insert",
            payload={
                "id": str(task_id),
                "user_id": str(user_id),
                "agenda_event_id": str(agenda_event_id) if agenda_event_id else None,
                "cliente_nome": cliente_nome,
                "cliente_numero": cliente_numero,
                "scheduled_for": str(scheduled_for),
                "status": "pending",
            },
        )
        return task_id

    async def list_tasks(
        self,
        db: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        await self.ensure_table(db)
        where = "WHERE user_id = CAST(:user_id AS UUID)"
        params: Dict[str, Any] = {"user_id": str(user_id)}
        if status:
            where += " AND status = :status"
            params["status"] = status

        count_row = await db.execute(
            text(f"SELECT COUNT(*) AS total FROM viva_handoff_tasks {where}"),
            params,
        )
        total = int(count_row.scalar() or 0)

        params["offset"] = (page - 1) * page_size
        params["limit"] = page_size
        rows = await db.execute(
            text(
                f"""
                SELECT id, user_id, agenda_event_id, cliente_nome, cliente_numero, mensagem,
                       scheduled_for, status, attempts, sent_at, last_error, meta_json, created_at, updated_at
                FROM viva_handoff_tasks
                {where}
                ORDER BY created_at DESC
                OFFSET :offset LIMIT :limit
                """
            ),
            params,
        )
        items = [dict(row._mapping) for row in rows.fetchall()]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    async def process_due_tasks(self, db: AsyncSession, limit: int = 20) -> Dict[str, Any]:
        await self.ensure_table(db)
        now = datetime.now(timezone.utc)
        rows = await db.execute(
            text(
                """
                SELECT id, cliente_numero, mensagem
                FROM viva_handoff_tasks
                WHERE status = 'pending' AND scheduled_for <= :now
                ORDER BY scheduled_for ASC
                LIMIT :limit
                """
            ),
            {"now": now, "limit": max(1, min(limit, 100))},
        )
        due = rows.fetchall()
        if not due:
            return {"processed": 0, "sent": 0, "failed": 0}

        wa = WhatsAppService()
        sent = 0
        failed = 0

        for row in due:
            task_id = row.id
            numero = str(row.cliente_numero or "").strip()
            mensagem = str(row.mensagem or "").strip()

            result = await wa.send_text(numero=numero, mensagem=mensagem)
            success = bool(result.get("sucesso"))
            if success:
                sent += 1
                await db.execute(
                    text(
                        """
                        UPDATE viva_handoff_tasks
                        SET status = 'sent',
                            sent_at = NOW(),
                            attempts = attempts + 1,
                            updated_at = NOW(),
                            last_error = NULL
                        WHERE id = :id
                        """
                    ),
                    {"id": str(task_id)},
                )
            else:
                failed += 1
                await db.execute(
                    text(
                        """
                        UPDATE viva_handoff_tasks
                        SET status = 'failed',
                            attempts = attempts + 1,
                            updated_at = NOW(),
                            last_error = :last_error
                        WHERE id = :id
                        """
                    ),
                    {"id": str(task_id), "last_error": str(result.get("erro") or "erro de envio")},
                )

        await db.commit()
        cofre_memory_service.log_event(
            table_name="viva_handoff_tasks",
            action="process_due_tasks",
            payload={
                "processed": len(due),
                "sent": sent,
                "failed": failed,
            },
        )
        return {"processed": len(due), "sent": sent, "failed": failed}


viva_handoff_service = VivaHandoffService()
