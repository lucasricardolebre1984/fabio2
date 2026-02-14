"""VIVA chat orchestration service.

Extrai a orquestracao pesada do endpoint /chat para reduzir acoplamento em rota.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.config import settings
from app.services.viva_chat_domain_service import (
    BACKGROUND_ONLY_SUFFIX,
    _apply_campaign_defaults,
    _build_branded_background_prompt,
    _build_branded_background_prompt_compact,
    _build_campaign_quick_plan,
    _build_viva_concierge_messages,
    _collect_campaign_fields_from_context,
    _extract_cast_preference,
    _extract_campaign_brief_fields,
    _has_pending_campaign_brief,
    _is_greeting,
    _preferred_greeting,
    _generate_campaign_copy,
    _has_campaign_signal,
    _infer_campaign_fields_from_free_text,
    _infer_mode_from_context,
    _infer_mode_from_message,
    _is_campaign_reset_intent,
    _is_image_request,
    _is_logo_request,
    _mode_hint,
    _resolve_image_size_from_format,
)
from app.api.v1.viva_schemas import ChatResponse, MediaItem
from app.schemas.agenda import EventoCreate
from app.services.agenda_service import AgendaService
from app.services.google_calendar_service import google_calendar_service
from app.services.openai_service import openai_service
from app.services.viva_agenda_nlu_service import viva_agenda_nlu_service
from app.services.viva_chat_session_service import (
    append_chat_message,
    context_from_snapshot,
    ensure_chat_tables,
    load_chat_snapshot,
    resolve_chat_session,
    serialize_media_items,
)
from app.services.viva_handoff_service import viva_handoff_service
from app.services.viva_local_service import viva_local_service
from app.services.viva_memory_service import viva_memory_service
from app.services.viva_model_service import viva_model_service
from app.services.viva_chat_runtime_helpers_service import (
    _build_fallback_image_prompt,
    _build_image_prompt,
    _build_viviane_handoff_message,
    _extract_cliente_nome,
    _extract_handoff_custom_message,
    _extract_image_url,
    _extract_phone_candidate,
    _format_viviane_handoff_list,
    _handoff_status_from_text,
    _is_handoff_whatsapp_intent,
    _is_stackoverflow_error,
    _is_viviane_handoff_query_intent,
    _normalize_any_datetime,
    _sanitize_fake_asset_delivery_reply,
    _sanitize_idle_confirmations,
    _sanitize_unsolicited_capability_menu,
)
from app.services.viva_shared_service import (
    _clear_campaign_history,
    _derive_campaign_title,
    _normalize_key,
    _normalize_mode,
    _save_campaign_record,
)
from app.services.viva_skill_router_service import viva_skill_router_service

logger = logging.getLogger(__name__)


class VivaChatOrchestratorService:
    async def handle_chat_with_viva(self, request: Any, current_user: Any, db: Any):
        """Chat direto com a VIVA usando OpenAI como provedor institucional."""
        try:
            await ensure_chat_tables(db)

            modo = (
                _normalize_mode(request.modo)
                or _infer_mode_from_message(request.mensagem)
                or _infer_mode_from_context(request.contexto)
            )

            session_id = await resolve_chat_session(
                db=db,
                user_id=current_user.id,
                requested_session_id=request.session_id,
                modo=modo,
            )
            active_skill_meta: Dict[str, Any] = {}

            async def finalize(
                resposta: str,
                midia: Optional[List[MediaItem]] = None,
                meta: Optional[Dict[str, Any]] = None,
            ) -> ChatResponse:
                final_meta = {**active_skill_meta, **(meta or {})}
                await append_chat_message(
                    db=db,
                    session_id=session_id,
                    user_id=current_user.id,
                    tipo="ia",
                    conteudo=resposta,
                    modo=modo,
                    anexos=serialize_media_items(midia),
                    meta=final_meta,
                )
                if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                    await viva_memory_service.append_memory(
                        db=db,
                        user_id=current_user.id,
                        session_id=session_id,
                        tipo="ia",
                        conteudo=resposta,
                        modo=modo,
                        meta={"source": "viva_chat_finalize", **final_meta},
                    )
                return ChatResponse(resposta=resposta, midia=midia, session_id=session_id)

            await append_chat_message(
                db=db,
                session_id=session_id,
                user_id=current_user.id,
                tipo="usuario",
                conteudo=request.mensagem,
                modo=modo,
                meta={"contexto_len": len(request.contexto or [])},
            )
            if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                await viva_memory_service.append_memory(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    tipo="usuario",
                    conteudo=request.mensagem,
                    modo=modo,
                    meta={"source": "viva_chat_input"},
                )

            snapshot = await load_chat_snapshot(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                # Menor janela reduz latencia do prompt (streaming ainda pendente).
                limit=90,
            )
            contexto_efetivo = context_from_snapshot(snapshot)
            if not modo:
                modo = _normalize_mode(snapshot.modo) or _infer_mode_from_context(contexto_efetivo)
            memory_context = None
            if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                memory_context = await viva_memory_service.build_chat_memory_context(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    query=request.mensagem,
                    modo=modo,
                )

            service = AgendaService(db)

            async def _sync_google_event_safe(evento: Any) -> None:
                try:
                    await google_calendar_service.sync_agenda_event(
                        db=db,
                        user_id=current_user.id,
                        evento=evento,
                    )
                except Exception as exc:
                    logger.warning(
                        "viva_chat_google_sync_failed evento=%s erro=%s",
                        str(getattr(evento, "id", "")),
                        str(exc)[:180],
                    )

            agenda_query_intent = viva_agenda_nlu_service.is_agenda_query_intent(request.mensagem, contexto_efetivo)
            agenda_command = viva_agenda_nlu_service.parse_agenda_command(request.mensagem)
            agenda_natural_command = viva_agenda_nlu_service.parse_agenda_natural_create(request.mensagem)
            agenda_errors: List[str] = []
            agenda_create_payload: Optional[Dict[str, Any]] = None
            handoff_intent = _is_handoff_whatsapp_intent(request.mensagem)
            viviane_handoff_query_intent = _is_viviane_handoff_query_intent(request.mensagem)
            logo_request = _is_logo_request(request.mensagem)

            if agenda_command is not None:
                if agenda_command.get("error"):
                    agenda_errors.append(str(agenda_command["error"]))
                else:
                    agenda_create_payload = agenda_command

            if not agenda_create_payload and agenda_natural_command is not None:
                if agenda_natural_command.get("error"):
                    agenda_errors.append(str(agenda_natural_command["error"]))
                else:
                    agenda_create_payload = agenda_natural_command

            active_skill_meta = viva_skill_router_service.resolve_skill(
                mensagem=request.mensagem,
                modo=modo,
                agenda_query_intent=agenda_query_intent,
                has_agenda_create_payload=bool(agenda_create_payload),
                handoff_intent=handoff_intent,
                viviane_handoff_query_intent=viviane_handoff_query_intent,
                campaign_flow_requested=False,
                should_generate_image=False,
                logo_request=logo_request,
            )

            if agenda_create_payload:
                evento = await service.create(
                    EventoCreate(
                        titulo=agenda_create_payload["title"],
                        descricao=agenda_create_payload.get("description"),
                        tipo=agenda_create_payload["tipo"],
                        data_inicio=agenda_create_payload["date_time"],
                        data_fim=None,
                        cliente_id=None,
                        contrato_id=None,
                    ),
                    current_user.id,
                )
                await _sync_google_event_safe(evento)

                if handoff_intent:
                    numero = _extract_phone_candidate(request.mensagem)
                    cliente_nome = _extract_cliente_nome(request.mensagem)
                    if not numero:
                        return await finalize(
                            resposta=(
                                "Agendamento criado com sucesso: "
                                f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}.\n"
                                "Para eu acionar a Viviane no horario, me passe o WhatsApp do cliente com DDD."
                            )
                        )

                    handoff_msg = (
                        _extract_handoff_custom_message(request.mensagem)
                        or _build_viviane_handoff_message(
                            cliente_nome=cliente_nome,
                            evento_titulo=evento.titulo,
                            data_inicio=evento.data_inicio,
                            modo=modo,
                        )
                    )
                    task_id = await viva_handoff_service.schedule_task(
                        db=db,
                        user_id=current_user.id,
                        cliente_nome=cliente_nome,
                        cliente_numero=numero,
                        mensagem=handoff_msg,
                        scheduled_for=evento.data_inicio,
                        agenda_event_id=evento.id,
                        meta={"source": "viva_chat", "session_id": str(session_id)},
                    )
                    return await finalize(
                        resposta=(
                            "Agendamento criado com sucesso: "
                            f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}.\n"
                            f"Handoff para Viviane agendado no WhatsApp (ID: {task_id})."
                        )
                    )

                return await finalize(
                    resposta=(
                        "Agendamento criado com sucesso: "
                        f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}."
                    )
                )

            conclude_command = viva_agenda_nlu_service.parse_agenda_conclude_command(request.mensagem)
            if conclude_command is not None:
                if conclude_command.get("error"):
                    return await finalize(
                        resposta=(
                            "Para concluir um compromisso, informe ID ou parte do titulo. "
                            "Exemplo: concluir reuniao com Fabio."
                        )
                    )

                target_event_id: Optional[UUID] = conclude_command.get("evento_id")
                search_text = str(conclude_command.get("search_text") or "").strip()
                if not target_event_id and search_text:
                    agenda_data = await service.list(
                        inicio=None,
                        fim=None,
                        concluido=False,
                        user_id=current_user.id,
                        page=1,
                        page_size=120,
                    )
                    items = list(agenda_data.get("items", []))
                    normalized_search = _normalize_key(search_text)
                    matches = [
                        item for item in items
                        if normalized_search in _normalize_key(getattr(item, "titulo", ""))
                    ]
                    if len(matches) == 1:
                        target_event_id = matches[0].id
                    elif len(matches) > 1:
                        sugestoes = "\n".join(
                            f"- {m.titulo} ({m.data_inicio.strftime('%d/%m %H:%M')})"
                            for m in matches[:3]
                        )
                        return await finalize(
                            resposta=(
                                "Encontrei mais de um compromisso parecido. Me diga qual deseja concluir:\n"
                                f"{sugestoes}"
                            )
                        )

                if not target_event_id:
                    return await finalize(resposta="Nao encontrei esse compromisso para concluir na sua agenda.")

                evento = await service.concluir(target_event_id, user_id=current_user.id)
                if not evento:
                    return await finalize(resposta="Nao encontrei esse compromisso para concluir na sua agenda.")
                await _sync_google_event_safe(evento)
                return await finalize(
                    resposta=(
                        "Compromisso concluido com sucesso: "
                        f"{evento.titulo} ({evento.data_inicio.strftime('%d/%m/%Y %H:%M')})."
                    )
                )

            if viviane_handoff_query_intent:
                inicio, fim, period_label = viva_agenda_nlu_service.agenda_window_from_text(request.mensagem)
                status_filter = _handoff_status_from_text(request.mensagem)
                handoff_data = await viva_handoff_service.list_tasks(
                    db=db,
                    user_id=current_user.id,
                    status=status_filter,
                    page=1,
                    page_size=200,
                )
                tasks = list(handoff_data.get("items", []))
                filtered_tasks: List[Dict[str, Any]] = []
                for task in tasks:
                    scheduled_for = _normalize_any_datetime(task.get("scheduled_for"))
                    if not scheduled_for:
                        continue
                    if inicio <= scheduled_for < fim:
                        filtered_tasks.append(task)
                return await finalize(resposta=_format_viviane_handoff_list(filtered_tasks, period_label, status_filter))

            if agenda_query_intent:
                inicio, fim, period_label = viva_agenda_nlu_service.agenda_window_from_text(request.mensagem)
                agenda_data = await service.list(
                    inicio=inicio,
                    fim=fim,
                    concluido=None,
                    user_id=current_user.id,
                    page=1,
                    page_size=120,
                )
                items = list(agenda_data.get("items", []))
                return await finalize(resposta=viva_agenda_nlu_service.format_agenda_list(items, period_label))

            if agenda_errors and (agenda_command is not None or agenda_natural_command is not None):
                return await finalize(
                    resposta=viva_agenda_nlu_service.build_agenda_recovery_reply(
                        request.mensagem,
                        agenda_errors,
                    )
                )

            # Cumprimento simples: resposta curta e sem acionar fluxo de campanha/imagem.
            if (
                _is_greeting(request.mensagem)
                and not handoff_intent
                and not viviane_handoff_query_intent
                and not logo_request
                and not agenda_query_intent
                and agenda_command is None
                and agenda_natural_command is None
            ):
                pending_campaign = bool(modo in ("FC", "REZETA") and _has_pending_campaign_brief(contexto_efetivo))
                if pending_campaign:
                    return await finalize(
                        resposta=(
                            f"{_preferred_greeting(request.mensagem)} "
                            "Quer continuar a campanha anterior ou prefere outra tarefa?"
                        ),
                        meta={"greeting_short_circuit": True, "pending_campaign": True},
                    )
                return await finalize(
                    resposta=f"{_preferred_greeting(request.mensagem)} O que voce precisa agora?",
                    meta={"greeting_short_circuit": True},
                )

            # Memoria eterna (pinned) - somente por comando explicito.
            normalized_input = _normalize_key(request.mensagem or "")
            pinned_prefixes = (
                "memorizar:",
                "memoria:",
                "memoria eterna:",
                "salvar memoria:",
                "salvar na memoria:",
                "fixar memoria:",
            )
            if normalized_input.startswith(pinned_prefixes):
                raw = str(request.mensagem or "")
                payload = raw.split(":", 1)[1].strip() if ":" in raw else ""
                if not payload:
                    return await finalize(
                        resposta="O que devo memorizar? Use: memorizar: <texto curto>.",
                        meta={"pinned_missing_payload": True},
                    )

                saved = await viva_memory_service.append_memory(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    tipo="pinned",
                    conteudo=payload,
                    modo=modo,
                    meta={"pinned": True, "source": "explicit_command"},
                )
                return await finalize(
                    resposta="Memoria salva.",
                    meta={"pinned_saved": True, "memory_write": saved},
                )

            campaign_flow_requested = False
            campaign_fields: Dict[str, str] = {}
            campaign_prompt_source = request.mensagem
            reset_campaign_memory_intent = _is_campaign_reset_intent(request.mensagem)
            suggestion_first_intent = (
                "antes de gerar" in _normalize_key(request.mensagem)
                or "me de uma sugestao" in _normalize_key(request.mensagem)
                or "me de sugestao" in _normalize_key(request.mensagem)
            )

            if reset_campaign_memory_intent:
                deleted = await _clear_campaign_history(
                    db=db,
                    user_id=current_user.id,
                    modo=modo if modo in ("FC", "REZETA") else None,
                )
                return await finalize(
                    resposta=(
                        "Memoria de padrao de campanhas limpa com sucesso. "
                        f"Itens removidos: {deleted}. "
                        "Agora vou seguir somente o contexto do seu pedido atual."
                    ),
                    meta={"campaign_history_cleared": deleted},
                )

            if modo in ("FC", "REZETA") and not logo_request:
                pending_campaign = _has_pending_campaign_brief(contexto_efetivo)
                campaign_fields = _collect_campaign_fields_from_context(contexto_efetivo)
                has_campaign_signal = _has_campaign_signal(request.mensagem)
                inferred_fields = (
                    _infer_campaign_fields_from_free_text(request.mensagem) if (has_campaign_signal or pending_campaign) else {}
                )
                explicit_fields = _extract_campaign_brief_fields(request.mensagem) if (has_campaign_signal or pending_campaign) else {}
                campaign_fields.update(explicit_fields)
                if has_campaign_signal:
                    campaign_fields.update(inferred_fields)
                campaign_flow_requested = has_campaign_signal or pending_campaign or bool(explicit_fields) or bool(inferred_fields)
                if campaign_flow_requested:
                    campaign_fields = _apply_campaign_defaults(campaign_fields)
                    # Fluxo livre: usar a mensagem original do usuario como fonte principal
                    # para nao impor estrutura fixa de briefing.
                    campaign_prompt_source = request.mensagem

            if (
                modo in ("FC", "REZETA")
                and campaign_flow_requested
                and not logo_request
                and suggestion_first_intent
                and not _is_image_request(request.mensagem)
            ):
                return await finalize(
                    resposta=_build_campaign_quick_plan(modo, campaign_fields),
                    meta={"campaign_suggestion_only": True},
                )

            should_generate_image = _is_image_request(request.mensagem) or (
                campaign_flow_requested
                and _has_campaign_signal(request.mensagem)
                and not suggestion_first_intent
                and not _is_greeting(request.mensagem)
            )
            active_skill_meta = viva_skill_router_service.resolve_skill(
                mensagem=request.mensagem,
                modo=modo,
                agenda_query_intent=agenda_query_intent,
                has_agenda_create_payload=bool(agenda_create_payload),
                handoff_intent=handoff_intent,
                viviane_handoff_query_intent=viviane_handoff_query_intent,
                campaign_flow_requested=campaign_flow_requested,
                should_generate_image=should_generate_image,
                logo_request=logo_request,
            )

            if should_generate_image:
                if not settings.OPENAI_API_KEY:
                    return await finalize(resposta="A geracao de imagens esta indisponivel no momento.")

                if not logo_request and modo not in ("FC", "REZETA"):
                    # Fluxo a prova de erro: para campanhas/imagens de marca, exige FC/Rezeta explicito.
                    return await finalize(resposta="Para essa campanha/imagem, voce quer FC ou Rezeta?")

                effective_mode = "LOGO" if logo_request else modo
                hint = _mode_hint(effective_mode)
                campaign_copy: Optional[Dict[str, Any]] = None
                image_size = "1024x1024"
                variation_id = uuid4().hex[:10]

                if effective_mode in ("FC", "REZETA"):
                    campaign_copy = await _generate_campaign_copy(
                        campaign_prompt_source,
                        None,
                        effective_mode,
                    )
                    cast_preference = _extract_cast_preference(campaign_prompt_source)
                    campaign_copy["cast_user_preference"] = cast_preference or str(
                        campaign_copy.get("cast_user_preference") or ""
                    )
                    image_size = _resolve_image_size_from_format(str(campaign_copy.get("formato") or "4:5"))
                    prompt = _build_branded_background_prompt(
                        effective_mode,
                        campaign_copy,
                        variation_id=variation_id,
                    )
                else:
                    prompt = _build_image_prompt(None, hint, request.mensagem)
                    prompt = f"{prompt}\n{BACKGROUND_ONLY_SUFFIX}"

                image_quality = "high" if effective_mode in ("FC", "REZETA") else None
                resultado = await openai_service.generate_image(prompt=prompt, size=image_size, quality=image_quality)
                if not resultado.get("success"):
                    erro = resultado.get("error")
                    if _is_stackoverflow_error(erro):
                        if effective_mode in ("FC", "REZETA") and campaign_copy:
                            fallback_prompt = _build_branded_background_prompt_compact(
                                effective_mode,
                                campaign_copy,
                                variation_id=f"{variation_id}-compact",
                            )
                        else:
                            fallback_prompt = _build_fallback_image_prompt(hint, request.mensagem)
                            fallback_prompt = f"{fallback_prompt}\n{BACKGROUND_ONLY_SUFFIX}"
                        resultado = await openai_service.generate_image(
                            prompt=fallback_prompt,
                            size=image_size,
                            quality=image_quality,
                        )
                        if resultado.get("success"):
                            url = _extract_image_url(resultado)
                            if url:
                                media_meta = {"overlay": campaign_copy} if campaign_copy else {}
                                resposta_texto = "Imagem gerada com sucesso."
                                if effective_mode in ("FC", "REZETA"):
                                    saved_id = await _save_campaign_record(
                                        db=db,
                                        user_id=current_user.id,
                                        modo=effective_mode,
                                        image_url=url,
                                        titulo=_derive_campaign_title(effective_mode, campaign_copy, request.mensagem),
                                        briefing=campaign_prompt_source,
                                        mensagem_original=request.mensagem,
                                        overlay=campaign_copy or {},
                                        meta={
                                            "source": "viva_chat",
                                            "size": image_size,
                                            "fallback": True,
                                        },
                                    )
                                    if saved_id:
                                        media_meta["campanha_id"] = str(saved_id)
                                        resposta_texto = "Imagem gerada com sucesso e salva em Campanhas."
                                media = MediaItem(tipo="imagem", url=url, meta=media_meta or None)
                                return await finalize(
                                    resposta=resposta_texto,
                                    midia=[media],
                                    meta={"effective_mode": effective_mode, "fallback": True},
                                )
                            return await finalize(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

                    msg = erro.get("message", "Erro desconhecido") if isinstance(erro, dict) else str(erro)
                    return await finalize(resposta=f"Erro ao gerar imagem: {msg}")

                url = _extract_image_url(resultado)
                if url:
                    media_meta = {"overlay": campaign_copy} if campaign_copy else {}
                    resposta_texto = "Imagem gerada com sucesso."
                    if effective_mode in ("FC", "REZETA"):
                        saved_id = await _save_campaign_record(
                            db=db,
                            user_id=current_user.id,
                            modo=effective_mode,
                            image_url=url,
                            titulo=_derive_campaign_title(effective_mode, campaign_copy, request.mensagem),
                            briefing=campaign_prompt_source,
                            mensagem_original=request.mensagem,
                            overlay=campaign_copy or {},
                            meta={
                                "source": "viva_chat",
                                "size": image_size,
                                "fallback": False,
                            },
                        )
                        if saved_id:
                            media_meta["campanha_id"] = str(saved_id)
                            resposta_texto = "Imagem gerada com sucesso e salva em Campanhas."
                    media = MediaItem(tipo="imagem", url=url, meta=media_meta)
                    return await finalize(
                        resposta=resposta_texto,
                        midia=[media],
                        meta={"effective_mode": effective_mode, "fallback": False},
                    )
                return await finalize(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

            if not settings.OPENAI_API_KEY:
                messages = viva_local_service.build_messages(request.mensagem, contexto_efetivo)
                resposta = await viva_local_service.chat(messages, modo)
            else:
                messages = _build_viva_concierge_messages(
                    mensagem=request.mensagem,
                    contexto=contexto_efetivo,
                    modo=modo,
                    memory_context=memory_context,
                )
                resposta = await viva_model_service.chat(
                    messages=messages,
                    temperature=0.45,
                    max_tokens=220,
                )
                if not resposta or resposta.strip().lower().startswith(("erro", "error")):
                    messages_local = viva_local_service.build_messages(request.mensagem, contexto_efetivo)
                    resposta = await viva_local_service.chat(messages_local, modo)

            resposta = _sanitize_idle_confirmations(resposta)
            resposta = _sanitize_unsolicited_capability_menu(request.mensagem, resposta)
            resposta = _sanitize_fake_asset_delivery_reply(resposta, modo)
            return await finalize(resposta=resposta)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")




    async def handle_chat_with_viva_stream(self, request: Any, current_user: Any, db: Any):
        """Chat com VIVA usando streaming de resposta (SSE).
        
        NOTA: Versão simplificada focada em chat textual.
        Para geração de imagens/campanhas, usa o endpoint não-streaming.
        """
        try:
            await ensure_chat_tables(db)

            modo = (
                _normalize_mode(request.modo)
                or _infer_mode_from_message(request.mensagem)
                or _infer_mode_from_context(request.contexto)
            )

            session_id = await resolve_chat_session(
                db=db,
                user_id=current_user.id,
                requested_session_id=request.session_id,
                modo=modo,
            )

            # Persistir mensagem do usuário
            await append_chat_message(
                db=db,
                session_id=session_id,
                user_id=current_user.id,
                tipo="usuario",
                conteudo=request.mensagem,
                modo=modo,
                meta={"contexto_len": len(request.contexto or [])},
            )

            if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                await viva_memory_service.append_memory(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    tipo="usuario",
                    conteudo=request.mensagem,
                    modo=modo,
                    meta={"source": "viva_chat_stream_input"},
                )

            # Carregar snapshot (limite reduzido para streaming - Gate 2)
            MAX_CONTEXT_MESSAGES = 10
            snapshot = await load_chat_snapshot(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                limit=MAX_CONTEXT_MESSAGES * 2,  # Considerando user+ia alternados
            )
            contexto_efetivo = context_from_snapshot(snapshot)

            if not modo:
                modo = _normalize_mode(snapshot.modo) or _infer_mode_from_context(contexto_efetivo)

            # Memória opcional
            memory_context = None
            if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                memory_context = await viva_memory_service.build_chat_memory_context(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    query=request.mensagem,
                    modo=modo,
                )

            # Preparar mensagens para o modelo
            if not settings.OPENAI_API_KEY:
                yield {"error": "OPENAI_API_KEY não configurada para streaming"}
                return

            messages = _build_viva_concierge_messages(
                mensagem=request.mensagem,
                contexto=contexto_efetivo,
                modo=modo,
                memory_context=memory_context,
            )

            # Stream da resposta
            full_response = ""
            async for chunk in openai_service.chat_stream(
                messages=messages,
                temperature=0.45,
                max_tokens=220,
            ):
                full_response += chunk
                yield {"content": chunk}

            # Sinalizar fim do streaming
            yield {"done": True, "session_id": str(session_id)}

            # Persistir resposta completa
            await append_chat_message(
                db=db,
                session_id=session_id,
                user_id=current_user.id,
                tipo="ia",
                conteudo=full_response,
                modo=modo,
                anexos=None,
                meta={"stream": True},
            )

            if bool(getattr(settings, "VIVA_MEMORY_ENABLED", False)):
                await viva_memory_service.append_memory(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    tipo="ia",
                    conteudo=full_response,
                    modo=modo,
                    meta={"source": "viva_chat_stream_finalize"},
                )

        except Exception as e:
            logger.error(f"Erro no streaming VIVA: {str(e)}")
            yield {"error": f"Erro: {str(e)}"}


viva_chat_orchestrator_service = VivaChatOrchestratorService()
