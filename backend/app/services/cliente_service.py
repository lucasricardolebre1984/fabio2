"""Cliente service - Business logic for clients."""
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.contrato import Contrato
from app.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteService:
    """Service for client management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: ClienteCreate) -> Cliente:
        """Create a new client."""
        cliente = Cliente(
            nome=data.nome,
            tipo_pessoa=data.tipo_pessoa,
            documento=data.documento,
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
        query = select(Cliente)
        
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
        items = result.scalars().all()
        
        return {
            "items": list(items),
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
            select(Cliente).where(
                func.replace(
                    func.replace(
                        func.replace(Cliente.documento, ".", ""),
                        "-", ""
                    ),
                    "/", ""
                ) == doc_clean
            )
        )
        return result.scalar_one_or_none()
    
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
        touched_client_ids = set()

        for contrato in contratos_orfaos:
            documento = self._normalize_document(contrato.contratante_documento or "")
            if not documento:
                skipped += 1
                continue

            cliente_result = await self.db.execute(
                select(Cliente).where(
                    func.replace(
                        func.replace(
                            func.replace(Cliente.documento, ".", ""),
                            "-",
                            "",
                        ),
                        "/",
                        "",
                    ) == documento
                )
            )
            cliente = cliente_result.scalar_one_or_none()

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
            touched_client_ids.add(cliente.id)
            linked += 1

        if touched_client_ids:
            for client_id in touched_client_ids:
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
                if cliente:
                    cliente.total_contratos = int(total or 0)
                    cliente.primeiro_contrato_em = primeiro
                    cliente.ultimo_contrato_em = ultimo

        await self.db.commit()

        return {
            "contratos_orfaos": len(contratos_orfaos),
            "clientes_criados": created,
            "contratos_vinculados": linked,
            "ignorados": skipped,
        }
    
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
