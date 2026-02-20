"""
VIVA - Assistente Virtual Inteligente
Integracao com OpenAI para atendimento de WhatsApp.
"""
from datetime import datetime, timezone
import logging
import re
import unicodedata
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp_conversa import TipoOrigem, WhatsappConversa, WhatsappMensagem
from app.services.viva_model_service import viva_model_service
from app.services.viva_knowledge_service import ServiceInfo, viva_knowledge_service


class VivaIAService:
    """VIVA - atendimento comercial humanizado da Rezeta no WhatsApp."""

    def __init__(self) -> None:
        self.base_system_prompt = """Voce e Viviane, consultora de negocios da Rezeta.
Nunca use linguagem robotica e nunca abra conversa dizendo que e IA.

MODO DE OPERACAO: B
- Conduza quase todo o atendimento.
- Escale para humano apenas nas regras de excecao.

PERSONA E TOM:
- Tom hibrido: consultivo, direto, cordial, simples e acolhedor.
- Evite cliches e respostas enlatadas.
- Responda de forma curta (1 a 4 linhas), com uma pergunta por vez.
- Se o cliente estiver formal, pode usar resposta mais completa com resumo.
- Priorize naturalidade: responda primeiro ao que o cliente acabou de perguntar.
- Evite insistencia: nao repetir a mesma pergunta de cadastro em toda mensagem.
- Se o cliente demonstrar cansaco/desinteresse, desacelere e ofereca saida elegante.

FLUXO COMERCIAL OBRIGATORIO:
1) Objetivo do cliente.
2) Perfil e contexto.
3) Urgencia.
4) Proximo passo claro.

DADOS OBRIGATORIOS DA QUALIFICACAO:
- nome, telefone, servico desejado, cidade e urgencia.
- Se faltar dado, faca uma pergunta objetiva para coletar.

REGRAS DE NEGOCIO:
- Nao prometer taxa, prazo, aprovacao ou condicao sem validacao humana.
- Nao inventar informacao juridica/financeira.
- Em caso sensivel, orientar e escalar.
- Se cliente perguntar se voce e IA, responda como Viviane de forma natural,
  sem negar de forma seca e sem confirmar tecnicamente.

REGRAS COMERCIAIS:
- Recomendar Diagnostico 360 como primeiro passo padrao.
- Excecao de venda direta: Limpa Nome, Aumento de Score e Rating.
- Oferta inicial considera margem de 15% na tabela de referencia.
- Negociacao final de desconto/condicao e com atendimento humano.
- Quando cliente nao fecha por preco, registrar no contexto como financeiro.

ESCALA PARA HUMANO:
- pedido explicito de humano;
- reclamacao;
- urgencia critica;
- duvida juridica/financeira sensivel;
- negociacao de valor;
- servico complexo em fechamento;
- assunto fora do catalogo oficial.
"""

        self.identity_replies = [
            "Sou a Viviane, consultora da Rezeta, e vou cuidar do seu atendimento.",
            "Aqui e a Viviane, da Rezeta. Me conta seu objetivo que eu te ajudo.",
            "Sou a Viviane, consultora de negocios da Rezeta. Vamos resolver isso juntas.",
            "Viviane falando, da Rezeta. Pode me explicar seu caso que eu te oriento.",
        ]

        self.handoff_keywords = {
            "quero falar com atendente",
            "falar com humano",
            "falar com gerente",
            "reclamacao",
            "reclamar",
            "procon",
            "processo",
            "advogado",
            "urgente",
            "hoje ainda",
            "agora",
            "desconto",
            "negociar valor",
            "nao consigo pagar",
            "duvida juridica",
            "duvida financeira sensivel",
        }

        self.formal_keywords = {
            "prezado",
            "prezada",
            "cordialmente",
            "gostaria",
            "solicito",
            "informo",
            "senhor",
            "senhora",
            "formalmente",
        }

        self.greeting_keywords = {
            "oi",
            "ola",
            "opa",
            "hello",
            "e ai",
            "bom dia",
            "boa tarde",
            "boa noite",
        }

        self.financial_objection_keywords = {
            "caro",
            "ta caro",
            "está caro",
            "sem dinheiro",
            "nao consigo pagar",
            "não consigo pagar",
            "fora do meu orcamento",
            "fora do meu orçamento",
            "sem condicao",
            "sem condição",
            "preco alto",
            "valor alto",
        }

        self.close_intent_keywords = {
            "quero contratar",
            "quero fechar",
            "vamos fechar",
            "vou contratar",
            "quero pagar",
            "como faco o pagamento",
            "como faço o pagamento",
            "vamos pagar",
        }

        self.disengage_keywords = {
            "nao quero mais",
            "não quero mais",
            "vou procurar outra empresa",
            "vou procurar outra",
            "pode cancelar",
            "cancela",
            "encerrar atendimento",
            "nao tenho interesse",
            "não tenho interesse",
            "desisto",
        }

        self.frustration_keywords = {
            "insistente",
            "insistente",
            "enrolando",
            "nao enrola",
            "não enrola",
            "nao invente",
            "não invente",
            "voce nao sabe",
            "você não sabe",
            "isso e robo",
            "isso é robô",
            "parece robo",
            "parece robô",
        }

        self.urgency_patterns = {
            "alta": ("urgente", "hoje", "agora", "imediato", "imediata"),
            "media": ("essa semana", "rapido", "rápido", "breve"),
            "baixa": ("sem pressa", "quando der", "pode ser depois"),
        }

    async def processar_mensagem(
        self,
        numero: str,
        mensagem: str,
        conversa: WhatsappConversa,
        db: AsyncSession,
    ) -> str:
        """Processa mensagem do usuario e gera resposta da Viviane."""
        viva_knowledge_service.refresh_if_changed()
        texto = self._normalizar(mensagem)
        contexto = dict(conversa.contexto_ia or {})
        lead = dict(contexto.get("lead") or {})
        lead.setdefault("telefone", self._format_phone(numero))

        nome_existente = str(lead.get("nome") or "").strip()
        if nome_existente and not self._limpar_nome(nome_existente):
            lead.pop("nome", None)
            if contexto.get("fase") == "atendimento":
                contexto["fase"] = "aguardando_nome"
        contexto.setdefault("conversation_mode", "qualificacao")

        self._atualizar_dados_lead(lead=lead, texto_original=mensagem, texto_normalizado=texto)
        service_info = viva_knowledge_service.find_service_from_message(mensagem)
        servico_inferido: Optional[str] = None
        if service_info:
            lead["servico"] = service_info.name
        elif not str(lead.get("servico") or "").strip():
            servico_inferido = self._inferir_servico_basico(texto)
            if servico_inferido:
                lead["servico"] = servico_inferido

        if self._eh_pergunta_identidade_ia(texto):
            resposta = self._resposta_identidade_variada(contexto)
            contexto["lead"] = lead
            conversa.contexto_ia = contexto
            await db.commit()
            return resposta

        if self._is_disengage_intent(texto):
            if self._tem_objeccao_financeira(texto):
                contexto["motivo_nao_fechamento"] = "financeiro"
            else:
                contexto["motivo_nao_fechamento"] = "desistencia"
            contexto["status_followup"] = "encerrado"
            contexto["lead"] = lead
            conversa.contexto_ia = contexto
            await db.commit()
            return (
                "Entendo e respeito sua decisao. Obrigada pelo seu tempo. "
                "Se mudar de ideia, eu te atendo por aqui sem burocracia."
            )

        if self._deve_escalar_para_humano(texto):
            contexto["lead"] = lead
            contexto["ultima_escala"] = datetime.now(timezone.utc).isoformat()
            contexto["conversation_mode"] = "descompressao"
            conversa.contexto_ia = contexto
            await db.commit()
            return (
                "Perfeito, vou te encaminhar para atendimento humano agora. "
                "Se puder, me resume em uma frase o que precisa para agilizar."
            )

        fase = contexto.get("fase", "inicio")

        if fase == "inicio":
            contexto["fase"] = "aguardando_nome"
            contexto["lead"] = lead
            conversa.contexto_ia = contexto
            await db.commit()

            if self._eh_saudacao_curta(texto):
                return f"{self._saudacao_horario()}! Tudo bem? Com quem eu falo?"
            return (
                f"{self._saudacao_horario()}! Para te atender de forma personalizada, "
                "com quem eu falo?"
            )

        if fase == "aguardando_nome":
            nome = self._extrair_nome(mensagem)
            if nome:
                lead["nome"] = nome
                contexto["nome_cliente"] = nome
                contexto["fase"] = "atendimento"
                contexto["conversation_mode"] = "qualificacao"
                contexto["lead"] = lead
                conversa.nome_contato = nome
                conversa.contexto_ia = contexto
                await db.commit()
                return (
                    f"Prazer, {nome}! Sou a Viviane, consultora de negocios da Rezeta. "
                    "Me conta seu objetivo para eu te ajudar da melhor forma."
                )
            if self._is_social_identity_question(texto):
                contexto["lead"] = lead
                contexto["conversation_mode"] = "descompressao"
                conversa.contexto_ia = contexto
                await db.commit()
                return (
                    "Sou a Viviane, consultora de negocios da Rezeta. "
                    "Como voce prefere que eu te chame?"
                )
            return "Me diz seu nome, por favor, para eu seguir com seu atendimento."

        if self._is_who_am_i_query(texto):
            contexto["lead"] = lead
            conversa.contexto_ia = contexto
            await db.commit()
            return self._build_known_identity_reply(lead=lead, fallback_phone=self._format_phone(numero))

        if self._eh_saudacao_curta(texto):
            contexto["lead"] = lead
            conversa.contexto_ia = contexto
            await db.commit()
            nome = str(lead.get("nome") or contexto.get("nome_cliente") or "").strip()
            if nome:
                return f"Oi, {nome}! Tudo bem? Estou por aqui para te ajudar no que voce precisar."
            return "Oi! Tudo bem? Estou por aqui para te ajudar no que voce precisar."

        if self._is_price_question(texto):
            known_service = service_info or viva_knowledge_service.find_service_from_message(str(lead.get("servico") or ""))
            if known_service:
                contexto["lead"] = lead
                conversa.contexto_ia = contexto
                await db.commit()
                return (
                    f"A faixa inicial de {known_service.name} e {known_service.price_label}. "
                    "Se quiser, te explico em 1 minuto como funciona o processo."
                )

        if self._tem_objeccao_financeira(texto):
            contexto["motivo_nao_fechamento"] = "financeiro"
            contexto["status_followup"] = "pendente"

        if (
            service_info
            and service_info.should_handoff_when_closing
            and self._tem_intencao_fechamento(texto)
        ):
            contexto["lead"] = lead
            contexto["ultima_escala"] = datetime.now(timezone.utc).isoformat()
            conversa.contexto_ia = contexto
            await db.commit()
            return (
                f"Perfeito, para concluir {service_info.name} com seguranca, "
                "vou te conectar com a consultoria humana para fechamento."
            )

        if "diagnostico 360" in texto and self._tem_intencao_fechamento(texto):
            contexto["lead"] = lead
            contexto["ultima_escala"] = datetime.now(timezone.utc).isoformat()
            conversa.contexto_ia = contexto
            await db.commit()
            return (
                "Excelente escolha. Vou te encaminhar para o atendimento humano "
                "finalizar o Diagnostico 360 com voce agora."
            )

        faltantes = self._lead_missing_fields(lead)
        primeiro_faltante = faltantes[0] if faltantes else None
        if primeiro_faltante:
            last_field = str(contexto.get("last_missing_field") or "")
            streak = int(contexto.get("missing_field_streak") or 0)
            contexto["missing_field_streak"] = streak + 1 if last_field == primeiro_faltante else 1
            contexto["last_missing_field"] = primeiro_faltante
        else:
            contexto["missing_field_streak"] = 0
            contexto["last_missing_field"] = ""
        if self._is_user_frustrated(texto):
            contexto["conversation_mode"] = "descompressao"
        elif not faltantes:
            contexto["conversation_mode"] = "qualificacao"
        contexto["lead"] = lead
        conversa.contexto_ia = contexto
        await db.commit()

        if faltantes and self._is_user_frustrated(texto):
            return self._build_decompression_reply(lead=lead, faltantes=faltantes)

        historico = await self._get_historico(conversa, db)
        formal = self._eh_formal(texto)
        messages = self._montar_contexto(
            historico=historico,
            mensagem_atual=mensagem,
            nome_cliente=contexto.get("nome_cliente"),
            lead=lead,
            service_info=service_info,
            faltantes=faltantes,
            missing_field_streak=int(contexto.get("missing_field_streak") or 0),
            last_missing_field=str(contexto.get("last_missing_field") or ""),
        )
        resposta_modelo = await self._chamar_glm(messages, formal=formal)
        return self._garantir_resposta_texto(
            resposta_modelo,
            faltantes=faltantes,
            lead=lead,
            missing_field_streak=int(contexto.get("missing_field_streak") or 0),
        )

    def _normalizar(self, texto: str) -> str:
        return (texto or "").strip().lower()

    def _format_phone(self, numero: str) -> str:
        digits = "".join(ch for ch in (numero or "") if ch.isdigit())
        if digits and not digits.startswith("55"):
            digits = "55" + digits
        return digits

    def _saudacao_horario(self) -> str:
        hora = datetime.now(ZoneInfo("America/Sao_Paulo")).hour
        if hora < 12:
            return "Bom dia"
        if hora < 18:
            return "Boa tarde"
        return "Boa noite"

    def _eh_saudacao_curta(self, texto: str) -> bool:
        if not texto:
            return False
        if texto in self.greeting_keywords:
            return True
        return len(texto) <= 15 and any(item in texto for item in self.greeting_keywords)

    def _eh_pergunta_identidade_ia(self, texto: str) -> bool:
        patterns = (
            "voce e ia",
            "você é ia",
            "voce e um robo",
            "você é um robô",
            "e robo",
            "é robô",
            "atendimento automatico",
            "atendimento automático",
            "chatgpt",
            "inteligencia artificial",
            "inteligência artificial",
        )
        return any(pattern in texto for pattern in patterns)

    def _resposta_identidade_variada(self, contexto: Dict[str, object]) -> str:
        index = int(contexto.get("identity_reply_index", 0) or 0)
        resposta = self.identity_replies[index % len(self.identity_replies)]
        contexto["identity_reply_index"] = index + 1
        return resposta

    def _deve_escalar_para_humano(self, texto: str) -> bool:
        if not texto:
            return False
        return any(keyword in texto for keyword in self.handoff_keywords)

    def _is_disengage_intent(self, texto: str) -> bool:
        if not texto:
            return False
        return any(keyword in texto for keyword in self.disengage_keywords)

    def _is_who_am_i_query(self, texto: str) -> bool:
        if not texto:
            return False
        patterns = (
            "sabe quem sou eu",
            "quem sou eu",
            "voce sabe quem eu sou",
            "você sabe quem eu sou",
            "ja sabe quem sou",
            "já sabe quem sou",
        )
        return any(pattern in texto for pattern in patterns)

    def _is_social_identity_question(self, texto: str) -> bool:
        if not texto:
            return False
        patterns = (
            "e voce",
            "e você",
            "qual seu nome",
            "qual o seu nome",
            "como voce se chama",
            "como você se chama",
            "e o seu",
            "com quem eu falo",
            "quem fala",
        )
        return any(pattern in texto for pattern in patterns)

    def _is_price_question(self, texto: str) -> bool:
        if not texto:
            return False
        patterns = (
            "qual o valor",
            "qual e o valor",
            "quanto custa",
            "preco",
            "preço",
            "valor do",
            "valor da",
        )
        return any(pattern in texto for pattern in patterns)

    def _build_known_identity_reply(self, lead: Dict[str, str], fallback_phone: str) -> str:
        nome = str(lead.get("nome") or "").strip() or "sem nome confirmado"
        telefone = str(lead.get("telefone") or "").strip() or fallback_phone or "-"
        servico = str(lead.get("servico") or "").strip() or "ainda nao definido"
        return (
            f"Tenho voce cadastrada como \"{nome}\" "
            f"(telefone {telefone}, servico {servico}). "
            "Se quiser, atualizo algum dado agora."
        )

    def _tem_objeccao_financeira(self, texto: str) -> bool:
        return any(keyword in texto for keyword in self.financial_objection_keywords)

    def _is_user_frustrated(self, texto: str) -> bool:
        if not texto:
            return False
        return any(keyword in texto for keyword in self.frustration_keywords)

    def _tem_intencao_fechamento(self, texto: str) -> bool:
        return any(keyword in texto for keyword in self.close_intent_keywords)

    def _eh_formal(self, texto: str) -> bool:
        return any(keyword in texto for keyword in self.formal_keywords)

    def _inferir_servico_basico(self, texto_normalizado: str) -> Optional[str]:
        mapping = (
            ("Limpa Nome", ("limpa nome", "limpar meu nome", "nome sujo", "tirar nome", "tirar restricao")),
            ("Aumento de Score", ("aumento de score", "aumentar score", "subir score")),
            ("Rating", ("rating", "melhorar rating")),
            ("Diagnostico 360", ("diagnostico 360", "diagnostico", "analise 360", "analise completa")),
        )
        for servico, keywords in mapping:
            if any(keyword in texto_normalizado for keyword in keywords):
                return servico
        return None

    def _extrair_nome(self, texto: str) -> Optional[str]:
        if not texto:
            return None

        padroes = [
            r"meu nome\s+[eé]\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"eu sou\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"sou o\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"sou a\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"sou\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"aqui\s+[eé]\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"aqui\s+[eé]\s+o\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"aqui\s+[eé]\s+a\s+([a-zA-ZÀ-ÿ\s]{2,50})",
            r"^\s*([a-zA-ZÀ-ÿ]{2,30})\s+(?:qual|e voce|e você|e o seu|e o seu nome)",
            r"^\s*([a-zA-ZÀ-ÿ]{2,30})\s*$",
        ]
        for padrao in padroes:
            match = re.search(padrao, texto, flags=re.IGNORECASE)
            if match:
                candidato = re.sub(
                    r"\b(e\s+voce|e\s+você|qual\s+o\s+seu(?:\s+nome)?|qual\s+o\s+seu|com\s+quem\s+eu\s+falo)\b.*$",
                    "",
                    match.group(1),
                    flags=re.IGNORECASE,
                )
                candidato = re.sub(r"^\s*(o|a)\s+", "", candidato, flags=re.IGNORECASE)
                return self._limpar_nome(candidato)
        return self._limpar_nome(texto)

    def _limpar_nome(self, valor: str) -> Optional[str]:
        nome = re.sub(r"[^a-zA-ZÀ-ÿ\s]", " ", valor or "")
        nome = re.sub(r"\s+", " ", nome).strip()
        if not nome:
            return None

        palavras = nome.split(" ")
        if len(palavras) > 4:
            return None
        if any(len(p) < 2 for p in palavras):
            return None

        proibidos = {
            "quero",
            "preciso",
            "ajuda",
            "sim",
            "nao",
            "bom",
            "dia",
            "tarde",
            "noite",
            "ola",
            "oi",
        }
        if any(self._remover_acentos(p).lower() in proibidos for p in palavras):
            return None
        return " ".join(p.capitalize() for p in palavras)

    def _remover_acentos(self, texto: str) -> str:
        if not texto:
            return ""
        normalized = unicodedata.normalize("NFKD", texto)
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

    def _garantir_resposta_texto(
        self,
        resposta: object,
        faltantes: List[str],
        lead: Dict[str, str],
        missing_field_streak: int = 0,
    ) -> str:
        """Garante resposta textual valida para envio no WhatsApp."""
        texto = resposta.strip() if isinstance(resposta, str) else ""
        if texto and self._resposta_modelo_valida(texto):
            return texto

        if faltantes:
            labels = {
                "nome": "seu nome",
                "telefone": "seu telefone com DDD",
                "servico": "o servico desejado",
                "cidade": "sua cidade",
                "urgencia": "qual sua urgencia",
            }
            campo = labels.get(faltantes[0], faltantes[0])
            servico = str(lead.get("servico") or "").strip()
            if missing_field_streak >= 3:
                if servico:
                    return (
                        f"Sem pressa. Se fizer sentido para voce, seguimos seu caso de {servico} no seu tempo. "
                        f"Quando quiser, me passa {campo}."
                    )
                return (
                    "Sem pressa. Se quiser continuar depois, eu te ajudo daqui. "
                    f"Quando quiser, me passa {campo}."
                )
            if servico:
                return (
                    f"Perfeito. No seu caso de {servico}, "
                    f"me confirma {campo}, por favor."
                )
            return f"Perfeito. Para seguir seu atendimento, me confirma {campo}, por favor."

        return (
            "Perfeito, recebi sua mensagem. "
            "Me conta em uma frase seu objetivo para eu te orientar agora."
        )

    def _build_decompression_reply(self, lead: Dict[str, str], faltantes: List[str]) -> str:
        servico = str(lead.get("servico") or "").strip()
        campo = faltantes[0] if faltantes else "seu objetivo"
        labels = {
            "nome": "seu nome",
            "telefone": "seu telefone com DDD",
            "servico": "o servico desejado",
            "cidade": "sua cidade",
            "urgencia": "sua urgencia",
        }
        campo_label = labels.get(campo, campo)
        if servico:
            return (
                f"Sem problema, vamos direto no seu caso de {servico}. "
                f"Se quiser seguir agora, so me confirma {campo_label}. "
                "Se preferir, te passo para atendimento humano."
            )
        return (
            "Sem problema, vamos direto. "
            f"Se quiser seguir agora, so me confirma {campo_label}. "
            "Se preferir, te passo para atendimento humano."
        )

    def _resposta_modelo_valida(self, texto: str) -> bool:
        """Descarta saidas tecnicas/meta que nao devem ir para o cliente."""
        if not texto:
            return False

        normalized = self._remover_acentos(texto).lower()
        blocked_markers = (
            "analyze the user",
            "user says",
            "context:",
            "assistant response",
            "chain of thought",
            "step-by-step",
            "system prompt",
            "as an ai",
            "i would like to",
            "###",
            "```",
        )
        if any(marker in normalized for marker in blocked_markers):
            return False

        return len(texto) <= 1200

    def _atualizar_dados_lead(
        self,
        lead: Dict[str, str],
        texto_original: str,
        texto_normalizado: str,
    ) -> None:
        phone_match = re.search(r"(\+?55)?\s*\(?\d{2}\)?\s*9?\d{4}-?\d{4}", texto_original)
        if phone_match and not lead.get("telefone"):
            lead["telefone"] = self._format_phone(phone_match.group(0))

        city_patterns = [
            r"(?:sou de|moro em|cidade[:\s]+)\s*([A-Za-zÀ-ÿ\s]{2,40})",
        ]
        for pattern in city_patterns:
            city_match = re.search(pattern, texto_original, flags=re.IGNORECASE)
            if city_match:
                city = re.sub(r"\s+", " ", city_match.group(1)).strip(" .,-")
                if city:
                    lead["cidade"] = city.title()
                    break

        if "urgencia" in texto_normalizado and "urgencia" not in lead:
            lead["urgencia"] = "nao informada"

        if not lead.get("urgencia"):
            for label, keywords in self.urgency_patterns.items():
                if any(word in texto_normalizado for word in keywords):
                    lead["urgencia"] = label
                    break

    def _lead_missing_fields(self, lead: Dict[str, str]) -> List[str]:
        required = ["nome", "telefone", "servico", "cidade", "urgencia"]
        return [field for field in required if not str(lead.get(field, "")).strip()]

    async def _get_historico(
        self,
        conversa: WhatsappConversa,
        db: AsyncSession,
        limite: int = 12,
    ) -> List[Dict[str, str]]:
        """Busca historico recente da conversa."""
        stmt = (
            select(WhatsappMensagem)
            .where(WhatsappMensagem.conversa_id == conversa.id)
            .order_by(WhatsappMensagem.created_at.desc())
            .limit(limite)
        )
        result = await db.execute(stmt)
        mensagens = list(reversed(result.scalars().all()))

        historico: List[Dict[str, str]] = []
        for msg in mensagens:
            role = "user" if msg.tipo_origem == TipoOrigem.USUARIO else "assistant"
            historico.append({"role": role, "content": msg.conteudo})
        return historico

    def _montar_contexto(
        self,
        historico: List[Dict[str, str]],
        mensagem_atual: str,
        nome_cliente: Optional[str],
        lead: Dict[str, str],
        service_info: Optional[ServiceInfo],
        faltantes: List[str],
        missing_field_streak: int = 0,
        last_missing_field: str = "",
    ) -> List[Dict[str, str]]:
        """Monta contexto completo para o modelo."""
        contexto_cliente = f"Cliente em atendimento: {nome_cliente}." if nome_cliente else ""
        lead_block = (
            "Lead coletado: "
            f"nome={lead.get('nome') or '-'}, "
            f"telefone={lead.get('telefone') or '-'}, "
            f"servico={lead.get('servico') or '-'}, "
            f"cidade={lead.get('cidade') or '-'}, "
            f"urgencia={lead.get('urgencia') or '-'}."
        )
        faltantes_block = (
            "Dados faltantes obrigatorios: " + ", ".join(faltantes) + "."
            if faltantes
            else "Todos os dados obrigatorios foram coletados."
        )

        selected_service_block = ""
        if service_info:
            tipo = "simples" if service_info.is_simple else "complexo"
            selected_service_block = (
                f"Servico citado: {service_info.name}. "
                f"Faixa inicial para oferta: {service_info.price_label}. "
                f"Tipo do servico: {tipo}."
            )

        insistencia_block = (
            f"Nivel de repeticao da mesma pendencia: {missing_field_streak} "
            f"(campo atual: {last_missing_field or '-'})"
        )

        dynamic_rules = (
            "TABELA DE SERVICOS (faixa inicial com margem de 15%):\n"
            f"{viva_knowledge_service.prices_prompt_block()}\n\n"
            "Diretriz de proposta:\n"
            "- Para servicos simples (Limpa Nome, Score, Rating), pode conduzir venda direta.\n"
            "- Para servicos complexos, orientar e encaminhar fechamento humano no momento certo.\n"
            "- Diagnostico 360 deve ser sugerido como primeiro passo, salvo excecao de servico simples.\n"
            "- Responda primeiro ao que o cliente perguntou agora; depois conduza o proximo passo.\n"
            "- Se a mesma pendencia ja foi solicitada 2+ vezes, nao insistir de forma repetitiva."
        )
        if viva_knowledge_service.services_text:
            dynamic_rules = (
                f"{dynamic_rules}\n\n"
                "Contexto institucional resumido da Rezeta:\n"
                f"{viva_knowledge_service.services_text}"
            )

        system = (
            f"{self.base_system_prompt}\n\n"
            f"{dynamic_rules}\n\n"
            f"{contexto_cliente}\n{lead_block}\n{faltantes_block}\n{selected_service_block}\n{insistencia_block}"
        )

        messages = [{"role": "system", "content": system}]
        messages.extend(historico)
        ultima_user_igual = (
            bool(historico)
            and historico[-1].get("role") == "user"
            and str(historico[-1].get("content") or "").strip() == (mensagem_atual or "").strip()
        )
        if not ultima_user_igual:
            messages.append({"role": "user", "content": mensagem_atual})
        return messages

    async def _chamar_glm(self, messages: List[Dict[str, str]], formal: bool) -> str:
        """Chama o provedor de IA configurado para a VIVA."""
        try:
            if formal:
                return await viva_model_service.chat(
                    messages=messages,
                    temperature=0.45,
                    max_tokens=520,
                )
            return await viva_model_service.chat(
                messages=messages,
                temperature=0.58,
                max_tokens=360,
            )
        except Exception as exc:
            logging.error("Erro ao chamar provedor de IA da VIVA: %r", exc)
            return (
                "Tive uma instabilidade agora. "
                "Posso continuar por aqui ou te encaminho para um atendente humano."
            )


viva_service = VivaIAService()
