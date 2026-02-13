"""VIVA chat orchestration service.

Extrai a orquestracao pesada do endpoint /chat para reduzir acoplamento em rota.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.config import settings
from app.services.viva_chat_domain_service import (
    BACKGROUND_ONLY_SUFFIX,
    _apply_campaign_defaults,
    _build_branded_background_prompt,
    _build_campaign_quick_plan,
    _build_viva_concierge_messages,
    _collect_campaign_fields_from_context,
    _extract_cast_preference,
    _ensure_fabio_greeting,
    _extract_campaign_brief_fields,
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
    _select_cast_profile,
    _select_scene_profile,
)
from app.api.v1.viva_schemas import ChatResponse, MediaItem
from app.schemas.agenda import EventoCreate
from app.services.agenda_service import AgendaService
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
)
from app.services.viva_shared_service import (
    _clear_campaign_history,
    _derive_campaign_title,
    _normalize_key,
    _normalize_mode,
    _save_campaign_record,
)


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

                async def finalize(
                    resposta: str,
                    midia: Optional[List[MediaItem]] = None,
                    meta: Optional[Dict[str, Any]] = None,
                ) -> ChatResponse:
                    await append_chat_message(
                        db=db,
                        session_id=session_id,
                        user_id=current_user.id,
                        tipo="ia",
                        conteudo=resposta,
                        modo=modo,
                        anexos=serialize_media_items(midia),
                        meta=meta or {},
                    )
                    await viva_memory_service.append_memory(
                        db=db,
                        user_id=current_user.id,
                        session_id=session_id,
                        tipo="ia",
                        conteudo=resposta,
                        modo=modo,
                        meta={"source": "viva_chat_finalize", **(meta or {})},
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
                    limit=180,
                )
                contexto_efetivo = context_from_snapshot(snapshot)
                if not modo:
                    modo = _normalize_mode(snapshot.modo) or _infer_mode_from_context(contexto_efetivo)
                memory_context = await viva_memory_service.build_chat_memory_context(
                    db=db,
                    user_id=current_user.id,
                    session_id=session_id,
                    query=request.mensagem,
                    modo=modo,
                )

                service = AgendaService(db)
                agenda_query_intent = viva_agenda_nlu_service.is_agenda_query_intent(request.mensagem, contexto_efetivo)
                agenda_command = viva_agenda_nlu_service.parse_agenda_command(request.mensagem)
                agenda_natural_command = viva_agenda_nlu_service.parse_agenda_natural_create(request.mensagem)
                agenda_errors: List[str] = []
                agenda_create_payload: Optional[Dict[str, Any]] = None

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
                    if _is_handoff_whatsapp_intent(request.mensagem):
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
                    return await finalize(
                        resposta=(
                            "Compromisso concluido com sucesso: "
                            f"{evento.titulo} ({evento.data_inicio.strftime('%d/%m/%Y %H:%M')})."
                        )
                    )

                viviane_handoff_query_intent = _is_viviane_handoff_query_intent(request.mensagem)
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
                    return await finalize(
                        resposta=_format_viviane_handoff_list(filtered_tasks, period_label, status_filter)
                    )

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

                campaign_flow_requested = False
                campaign_fields: Dict[str, str] = {}
                campaign_prompt_source = request.mensagem
                logo_request = _is_logo_request(request.mensagem)
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
                    campaign_fields = _collect_campaign_fields_from_context(contexto_efetivo)
                    inferred_fields = _infer_campaign_fields_from_free_text(request.mensagem)
                    explicit_fields = _extract_campaign_brief_fields(request.mensagem)
                    has_campaign_signal = _has_campaign_signal(request.mensagem)
                    campaign_fields.update(explicit_fields)
                    if has_campaign_signal:
                        campaign_fields.update(inferred_fields)
                    campaign_flow_requested = has_campaign_signal or bool(explicit_fields) or bool(inferred_fields)
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
                    and not suggestion_first_intent
                )

                if should_generate_image:
                    if not settings.OPENAI_API_KEY:
                        return await finalize(resposta="A geracao de imagens esta indisponivel no momento.")

                    effective_mode = "LOGO" if logo_request else modo
                    hint = _mode_hint(effective_mode)
                    campaign_copy: Optional[Dict[str, Any]] = None
                    image_size = "1024x1024"
                    variation_id = uuid4().hex[:10]

                    if effective_mode in ("FC", "REZETA"):
                        recent_cast_ids: List[str] = []
                        recent_scene_ids: List[str] = []
                        campaign_copy = await _generate_campaign_copy(
                            campaign_prompt_source,
                            None,
                            effective_mode,
                        )
                        cast_preference = _extract_cast_preference(campaign_prompt_source)
                        campaign_copy["cast_user_preference"] = cast_preference or str(
                            campaign_copy.get("cast_user_preference") or ""
                        )
                        cast_profile = _select_cast_profile(
                            seed=f"{variation_id}|{campaign_prompt_source}",
                            publico=str(campaign_copy.get("publico") or ""),
                            recent_cast_ids=recent_cast_ids,
                            cast_preference=cast_preference,
                        )
                        scene_profile = _select_scene_profile(
                            seed=f"{variation_id}|scene|{campaign_prompt_source}",
                            publico=str(campaign_copy.get("publico") or ""),
                            recent_scene_ids=recent_scene_ids,
                        )
                        campaign_copy["cast_profile"] = cast_profile
                        campaign_copy["recent_cast_ids"] = recent_cast_ids
                        campaign_copy["scene_profile"] = scene_profile
                        campaign_copy["recent_scene_ids"] = recent_scene_ids
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
                        temperature=0.58,
                        max_tokens=700,
                    )
                    if not resposta or resposta.strip().lower().startswith(("erro", "error")):
                        messages_local = viva_local_service.build_messages(request.mensagem, contexto_efetivo)
                        resposta = await viva_local_service.chat(messages_local, modo)

                resposta = _sanitize_fake_asset_delivery_reply(resposta, modo)
                resposta = _ensure_fabio_greeting(request.mensagem, resposta)
                return await finalize(resposta=resposta)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")




viva_chat_orchestrator_service = VivaChatOrchestratorService()
