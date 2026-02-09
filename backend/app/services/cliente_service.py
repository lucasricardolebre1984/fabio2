"""Cliente service - Business logic for clients."""
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from sqlalchemy import select, desc, func, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.contrato import Contrato
from app.models.agenda import Agenda
from app.schemas.cliente import ClienteCreate, ClienteUpdate

logger = logging.getLogger(__name__)


class ClienteService:
    """Service for client management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _document_expression():
        return func.regexp_replace(Cliente.documento, r"[^0-9]", "", "g")

    @staticmethod
    def _serialize_cliente(
        cliente: Cliente,
        total_contratos: Optional[int] = None,
        primeiro_contrato_em=None,
        ultimo_contrato_em=None,
    ) -> Dict[str, Any]:
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "tipo_pessoa": cliente.tipo_pessoa,
            "documento": cliente.documento,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "endereco": cliente.endereco,
            "cidade": cliente.cidade,
            "estado": cliente.estado,
            "cep": cliente.cep,
            "observacoes": cliente.observacoes,
            "total_contratos": int(
                total_contratos
                if total_contratos is not None
                else (cliente.total_contratos or 0)
            ),
            "primeiro_contrato_em": (
                primeiro_contrato_em
                if primeiro_contrato_em is not None
                else cliente.primeiro_contrato_em
            ),
            "ultimo_contrato_em": (
                ultimo_contrato_em
                if ultimo_contrato_em is not None
                else cliente.ultimo_contrato_em
            ),
            "created_at": cliente.created_at,
            "updated_at": cliente.updated_at,
        }

    async def create(self, data: ClienteCreate) -> Cliente:
        """Create a new client."""
        documento_normalizado = self._normalize_document(data.documento)
        cliente = Cliente(
            nome=data.nome,
            tipo_pessoa=data.tipo_pessoa,
            documento=documento_normalizado,
            email=data.email,
            telefone=data.telefone,
            endereco=data.endereco,
            cidade=data.cidade,
            estado=data.estado,
            cep=data.cep,
            observacoes=data.observacoes,
            total_contratos=0
        )
        
        self.db.add(cliente)
        await self.db.commit()
        await self.db.refresh(cliente)
        
        return cliente
    
    async def list(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List clients with pagination."""
        metrics_subquery = (
            select(
                Contrato.cliente_id.label("cliente_id"),
                func.count(Contrato.id).label("total_contratos_calculado"),
                func.min(Contrato.created_at).label("primeiro_contrato_em_calculado"),
                func.max(Contrato.created_at).label("ultimo_contrato_em_calculado"),
            )
            .where(Contrato.cliente_id.is_not(None))
            .group_by(Contrato.cliente_id)
            .subquery()
        )

        query = (
            select(
                Cliente,
                func.coalesce(metrics_subquery.c.total_contratos_calculado, 0).label(
                    "total_contratos_calculado"
                ),
                metrics_subquery.c.primeiro_contrato_em_calculado,
                metrics_subquery.c.ultimo_contrato_em_calculado,
            )
            .outerjoin(metrics_subquery, metrics_subquery.c.cliente_id == Cliente.id)
        )
        
        if search:
            query = query.where(
                or_(
                    Cliente.nome.ilike(f"%{search}%"),
                    Cliente.documento.ilike(f"%{search}%"),
                    Cliente.email.ilike(f"%{search}%")
                )
            )
        
        count_query = query.subquery()
        count_result = await self.db.execute(
            select(func.count()).select_from(count_query)
        )
        total = count_result.scalar()

        query = (
            query.order_by(desc(Cliente.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        rows = result.all()
        items = [
            self._serialize_cliente(
                cliente=cliente,
                total_contratos=total_contratos_calculado,
                primeiro_contrato_em=primeiro_contrato_em_calculado,
                ultimo_contrato_em=ultimo_contrato_em_calculado,
            )
            for (
                cliente,
                total_contratos_calculado,
                primeiro_contrato_em_calculado,
                ultimo_contrato_em_calculado,
            ) in rows
        ]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_by_id(self, cliente_id: UUID) -> Optional[Cliente]:
        """Get client by ID."""
        result = await self.db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_documento(self, documento: str) -> Optional[Cliente]:
        """Get client by documento (CPF/CNPJ)."""
        doc_clean = self._normalize_document(documento)

        result = await self.db.execute(
            select(Cliente)
            .where(self._document_expression() == doc_clean)
            .order_by(
                desc(Cliente.total_contratos),
                Cliente.created_at.asc(),
                Cliente.id.asc(),
            )
        )
        clientes = list(result.scalars().all())

        if len(clientes) > 1:
            logger.warning(
                "Duplicidade de cliente detectada para documento %s (%s registros).",
                doc_clean,
                len(clientes),
            )

        return clientes[0] if clientes else None
    
    async def update(self, cliente_id: UUID, data: ClienteUpdate) -> Optional[Cliente]:
        """Update client."""
        result = await self.db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(cliente, field, value)
        
        await self.db.commit()
        await self.db.refresh(cliente)
        
        return cliente
    
    async def delete(self, cliente_id: UUID) -> bool:
        """Delete client."""
        result = await self.db.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            return False
        
        await self.db.delete(cliente)
        await self.db.commit()
        
        return True
    
    async def get_contratos(self, cliente_id: UUID) -> List[Contrato]:
        """Get client contract history."""
        result = await self.db.execute(
            select(Contrato)
            .where(Contrato.cliente_id == cliente_id)
            .order_by(desc(Contrato.created_at))
        )
        return list(result.scalars().all())

    @staticmethod
    def _normalize_document(documento: str) -> str:
        return (
            (documento or "")
            .replace(".", "")
            .replace("-", "")
            .replace("/", "")
            .strip()
        )

    async def sync_from_contracts(self) -> Dict[str, int]:
        """
        Backfill clients from contracts that were created without proper linkage.
        """
        result = await self.db.execute(
            select(Contrato)
            .where(Contrato.cliente_id.is_(None))
            .order_by(desc(Contrato.created_at))
        )
        contratos_orfaos = list(result.scalars().all())

        created = 0
        linked = 0
        skipped = 0

        for contrato in contratos_orfaos:
            documento = self._normalize_document(contrato.contratante_documento or "")
            if not documento:
                skipped += 1
                continue

            cliente = await self.get_by_documento(documento)

            if not cliente:
                cliente = Cliente(
                    nome=contrato.contratante_nome,
                    tipo_pessoa="fisica" if len(documento) == 11 else "juridica",
                    documento=documento,
                    email=contrato.contratante_email,
                    telefone=contrato.contratante_telefone,
                    endereco=contrato.contratante_endereco,
                    primeiro_contrato_em=contrato.created_at,
                    ultimo_contrato_em=contrato.created_at,
                    total_contratos=0,
                )
                self.db.add(cliente)
                await self.db.flush()
                created += 1

            contrato.cliente_id = cliente.id
            linked += 1

        recalculados = await self._rebuild_all_metrics()

        await self.db.commit()

        return {
            "contratos_orfaos": len(contratos_orfaos),
            "clientes_criados": created,
            "contratos_vinculados": linked,
            "ignorados": skipped,
            "clientes_recalculados": recalculados,
        }

    async def deduplicate_documentos(self) -> Dict[str, int]:
        """
        Merge clients with the same normalized document and relink references.
        """
        doc_expr = self._document_expression()
        duplicates_result = await self.db.execute(
            select(
                doc_expr.label("documento_normalizado"),
                func.count(Cliente.id).label("total"),
            )
            .group_by(doc_expr)
            .having(func.count(Cliente.id) > 1)
        )
        duplicates = duplicates_result.all()

        grupos = 0
        removidos = 0
        contratos_relinkados = 0
        agenda_relinkada = 0

        for row in duplicates:
            documento_normalizado = row.documento_normalizado
            clientes_result = await self.db.execute(
                select(Cliente)
                .where(doc_expr == documento_normalizado)
                .order_by(
                    desc(Cliente.total_contratos),
                    Cliente.created_at.asc(),
                    Cliente.id.asc(),
                )
            )
            clientes = list(clientes_result.scalars().all())
            if len(clientes) <= 1:
                continue

            grupos += 1
            canonical = clientes[0]
            duplicates_to_remove = clientes[1:]

            for duplicate in duplicates_to_remove:
                # Preserve the richest available contact data on canonical record.
                if not canonical.telefone and duplicate.telefone:
                    canonical.telefone = duplicate.telefone
                if not canonical.endereco and duplicate.endereco:
                    canonical.endereco = duplicate.endereco
                if not canonical.cidade and duplicate.cidade:
                    canonical.cidade = duplicate.cidade
                if not canonical.estado and duplicate.estado:
                    canonical.estado = duplicate.estado
                if not canonical.cep and duplicate.cep:
                    canonical.cep = duplicate.cep
                if not canonical.observacoes and duplicate.observacoes:
                    canonical.observacoes = duplicate.observacoes

                contratos_update = await self.db.execute(
                    update(Contrato)
                    .where(Contrato.cliente_id == duplicate.id)
                    .values(cliente_id=canonical.id)
                )
                contratos_relinkados += int(contratos_update.rowcount or 0)

                agenda_update = await self.db.execute(
                    update(Agenda)
                    .where(Agenda.cliente_id == duplicate.id)
                    .values(cliente_id=canonical.id)
                )
                agenda_relinkada += int(agenda_update.rowcount or 0)

                await self.db.delete(duplicate)
                removidos += 1

            metrics_result = await self.db.execute(
                select(
                    func.count(Contrato.id),
                    func.min(Contrato.created_at),
                    func.max(Contrato.created_at),
                ).where(Contrato.cliente_id == canonical.id)
            )
            total, primeiro, ultimo = metrics_result.one()
            canonical.total_contratos = int(total or 0)
            canonical.primeiro_contrato_em = primeiro
            canonical.ultimo_contrato_em = ultimo

        await self.db.commit()

        return {
            "grupos_duplicados": grupos,
            "clientes_removidos": removidos,
            "contratos_relinkados": contratos_relinkados,
            "agenda_relinkada": agenda_relinkada,
        }

    async def _rebuild_all_metrics(self) -> int:
        """Recalculate contract metrics for every client."""
        result = await self.db.execute(select(Cliente.id))
        client_ids = [row[0] for row in result.all()]

        for client_id in client_ids:
            count_result = await self.db.execute(
                select(
                    func.count(Contrato.id),
                    func.min(Contrato.created_at),
                    func.max(Contrato.created_at),
                ).where(Contrato.cliente_id == client_id)
            )
            total, primeiro, ultimo = count_result.one()

            cliente_result = await self.db.execute(
                select(Cliente).where(Cliente.id == client_id)
            )
            cliente = cliente_result.scalar_one_or_none()
            if not cliente:
                continue

            cliente.total_contratos = int(total or 0)
            cliente.primeiro_contrato_em = primeiro
            cliente.ultimo_contrato_em = ultimo

        return len(client_ids)
    
    async def get_historico(self, cliente_id: UUID) -> Dict[str, Any]:
        """Get complete client timeline."""
        cliente = await self.get_by_id(cliente_id)
        if not cliente:
            return None
        
        contratos = await self.get_contratos(cliente_id)
        
        # Build timeline
        timeline = []
        
        # Add creation
        timeline.append({
            "tipo": "criacao",
            "data": cliente.created_at,
            "descricao": "Cliente cadastrado",
            "detalhes": None
        })
        
        # Add contracts
        for contrato in contratos:
            timeline.append({
                "tipo": "contrato",
                "data": contrato.created_at,
                "descricao": f"Contrato {contrato.numero} criado",
                "detalhes": {
                    "contrato_id": str(contrato.id),
                    "numero": contrato.numero,
                    "valor": str(contrato.valor_total),
                    "status": contrato.status.value
                }
            })
        
        # Sort by date
        timeline.sort(key=lambda x: x["data"], reverse=True)
        
        return {
            "cliente": cliente,
            "contratos": contratos,
            "timeline": timeline
        }
