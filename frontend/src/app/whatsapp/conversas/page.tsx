"use client";

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Archive, Bot, MessageCircle, RefreshCw, Send, User } from "lucide-react";

import { Sidebar } from "@/components/layout/Sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

interface Conversa {
  id: string;
  numero_telefone: string;
  nome_contato: string | null;
  instance_name: string;
  status: string;
  ultima_mensagem_em: string | null;
  created_at: string;
}

interface Mensagem {
  id: string;
  tipo_origem: "usuario" | "ia" | "sistema";
  conteudo: string;
  lida: boolean;
  enviada: boolean;
  created_at: string;
}

interface Stats {
  conversas_ativas: number;
  mensagens_hoje: number;
}

function WhatsAppConversasPageContent() {
  const searchParams = useSearchParams();
  const { toast } = useToast();

  const [conversas, setConversas] = useState<Conversa[]>([]);
  const [conversaSelecionada, setConversaSelecionada] = useState<Conversa | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingEnvio, setLoadingEnvio] = useState(false);
  const [novaMensagem, setNovaMensagem] = useState("");
  const [busca, setBusca] = useState("");
  const [stats, setStats] = useState<Stats>({ conversas_ativas: 0, mensagens_hoje: 0 });
  const [showingArchivedFallback, setShowingArchivedFallback] = useState(false);
  const [arquivandoIds, setArquivandoIds] = useState<Set<string>>(new Set());

  const carregarConversas = useCallback(async () => {
    try {
      const [ativasResp, aguardandoResp] = await Promise.all([
        api.get<Conversa[]>("/whatsapp-chat/conversas", { params: { status: "ativa", limit: 100 } }),
        api.get<Conversa[]>("/whatsapp-chat/conversas", { params: { status: "aguardando", limit: 100 } }),
      ]);

      const abertasMap = new Map<string, Conversa>();
      for (const conversa of [...ativasResp.data, ...aguardandoResp.data]) {
        abertasMap.set(conversa.id, conversa);
      }
      const abertas = Array.from(abertasMap.values());

      if (abertas.length > 0) {
        setConversas(abertas);
        setShowingArchivedFallback(false);
        return;
      }

      const arquivadasResp = await api.get<Conversa[]>("/whatsapp-chat/conversas", {
        params: { status: "arquivada", limit: 100 },
      });
      setConversas(arquivadasResp.data);
      setShowingArchivedFallback(arquivadasResp.data.length > 0);
    } catch (error) {
      console.error("Erro ao carregar conversas:", error);
    }
  }, []);

  const carregarStats = useCallback(async () => {
    try {
      const response = await api.get<Stats>("/whatsapp-chat/status");
      setStats(response.data);
    } catch (error) {
      console.error("Erro ao carregar stats:", error);
    }
  }, []);

  const carregarMensagens = useCallback(async (conversaId: string) => {
    try {
      const response = await api.get<Mensagem[]>(`/whatsapp-chat/conversas/${conversaId}/mensagens`);
      setMensagens(response.data);
    } catch (error) {
      console.error("Erro ao carregar mensagens:", error);
    }
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      await Promise.all([carregarConversas(), carregarStats()]);
      const newMessage = searchParams.get("newMessage");
      if (newMessage) {
        setNovaMensagem(newMessage);
      }
      setLoading(false);
    };
    bootstrap();
  }, [carregarConversas, carregarStats, searchParams]);

  useEffect(() => {
    const interval = setInterval(() => {
      carregarConversas();
      carregarStats();
      if (conversaSelecionada) {
        carregarMensagens(conversaSelecionada.id);
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [carregarConversas, carregarStats, carregarMensagens, conversaSelecionada]);

  const handleSelecionarConversa = async (conversa: Conversa) => {
    setConversaSelecionada(conversa);
    await carregarMensagens(conversa.id);
  };

  const handleArquivar = async (e: React.MouseEvent, conversa: Conversa) => {
    e.stopPropagation();
    e.preventDefault();

    if (conversa.status === "arquivada") {
      return;
    }

    if (arquivandoIds.has(conversa.id)) {
      return;
    }

    setArquivandoIds((prev) => {
      const next = new Set(prev);
      next.add(conversa.id);
      return next;
    });

    try {
      await api.post(`/whatsapp-chat/conversas/${conversa.id}/arquivar`);
      toast({ title: "Conversa arquivada" });
      await carregarConversas();
      await carregarStats();
      if (conversaSelecionada?.id === conversa.id) {
        setConversaSelecionada(null);
        setMensagens([]);
      }
    } catch (error) {
      toast({ title: "Erro ao arquivar", variant: "destructive" });
    } finally {
      setArquivandoIds((prev) => {
        const next = new Set(prev);
        next.delete(conversa.id);
        return next;
      });
    }
  };

  const handleEnviarMensagem = async () => {
    if (!conversaSelecionada) return;
    const conteudo = novaMensagem.trim();
    if (!conteudo) return;

    setLoadingEnvio(true);
    try {
      await api.post("/whatsapp/enviar-texto", null, {
        params: {
          numero: conversaSelecionada.numero_telefone,
          mensagem: conteudo,
        },
      });
      setNovaMensagem("");
      toast({ title: "Mensagem enviada no WhatsApp" });
      await carregarMensagens(conversaSelecionada.id);
      await carregarConversas();
      await carregarStats();
    } catch (error: any) {
      const detail = error?.response?.data?.detail || "Falha ao enviar mensagem";
      toast({
        title: "Erro no envio",
        description: String(detail),
        variant: "destructive",
      });
    } finally {
      setLoadingEnvio(false);
    }
  };

  const formatarNumero = (numero: string) => {
    if (numero.length === 13) {
      return `+${numero.slice(0, 2)} (${numero.slice(2, 4)}) ${numero.slice(4, 9)}-${numero.slice(9)}`;
    }
    return numero;
  };

  const formatarData = (data: string | null) => {
    if (!data) return "";
    const date = new Date(data);
    const agora = new Date();
    const diff = agora.getTime() - date.getTime();

    if (diff < 60000) return "Agora";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}min`;
    if (diff < 86400000) return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    return date.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
  };

  const conversasFiltradas = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    if (!termo) return conversas;
    return conversas.filter((conversa) => {
      const nome = (conversa.nome_contato || "").toLowerCase();
      const numero = conversa.numero_telefone.toLowerCase();
      return nome.includes(termo) || numero.includes(termo);
    });
  }, [busca, conversas]);

  if (loading) {
    return (
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <div className="flex flex-1 items-center justify-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="border-b bg-white px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
                <MessageCircle className="h-6 w-6 text-green-500" />
                Conversas WhatsApp
              </h1>
              <p className="mt-1 text-sm text-gray-500">Atendimento com IA VIVA</p>
            </div>

            <div className="flex gap-4">
              <Card className="px-4 py-2">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{stats.conversas_ativas}</div>
                  <div className="text-xs text-gray-500">Ativas</div>
                </div>
              </Card>
              <Card className="px-4 py-2">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{stats.mensagens_hoje}</div>
                  <div className="text-xs text-gray-500">Hoje</div>
                </div>
              </Card>
            </div>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          <div className="flex w-96 flex-col border-r bg-white">
            <div className="border-b p-4">
              <Input placeholder="Buscar conversa..." value={busca} onChange={(e) => setBusca(e.target.value)} />
            </div>

            <ScrollArea className="flex-1">
              {conversasFiltradas.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <MessageCircle className="mx-auto mb-4 h-12 w-12 text-gray-300" />
                  <p>Nenhuma conversa ativa</p>
                  <p className="mt-2 text-sm">As conversas aparecerao aqui quando clientes enviarem mensagens</p>
                </div>
              ) : (
                <div className="divide-y">
                  {showingArchivedFallback && (
                    <div className="border-b bg-amber-50 px-4 py-2 text-xs text-amber-800">
                      Exibindo conversas arquivadas (nenhuma conversa ativa no momento).
                    </div>
                  )}
                  {conversasFiltradas.map((conversa) => (
                    <div
                      key={conversa.id}
                      onClick={() => handleSelecionarConversa(conversa)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          handleSelecionarConversa(conversa);
                        }
                      }}
                      role="button"
                      tabIndex={0}
                      aria-label={`Abrir conversa de ${conversa.nome_contato || formatarNumero(conversa.numero_telefone)}`}
                      className={`w-full p-4 text-left transition-colors hover:bg-gray-50 ${
                        conversaSelecionada?.id === conversa.id ? "border-l-4 border-blue-500 bg-blue-50" : ""
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10 bg-blue-100">
                            <AvatarFallback className="text-sm text-blue-600">
                              {(conversa.nome_contato || conversa.numero_telefone).slice(0, 2).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium text-gray-900">
                              {conversa.nome_contato || formatarNumero(conversa.numero_telefone)}
                            </p>
                            <p className="text-sm text-gray-500">{formatarNumero(conversa.numero_telefone)}</p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          <span className="text-xs text-gray-400">{formatarData(conversa.ultima_mensagem_em)}</span>
                          <button
                            onClick={(e) => handleArquivar(e, conversa)}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-40"
                            aria-label={`Arquivar conversa de ${conversa.nome_contato || formatarNumero(conversa.numero_telefone)}`}
                            title="Arquivar"
                            disabled={conversa.status === "arquivada" || arquivandoIds.has(conversa.id)}
                          >
                            <Archive className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          <div className="flex flex-1 flex-col bg-gray-50">
            {conversaSelecionada ? (
              <>
                <div className="flex items-center justify-between border-b bg-white px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 bg-green-100">
                      <AvatarFallback className="text-green-600">
                        {(conversaSelecionada.nome_contato || conversaSelecionada.numero_telefone).slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {conversaSelecionada.nome_contato || formatarNumero(conversaSelecionada.numero_telefone)}
                      </h3>
                      <p className="text-sm text-gray-500">{formatarNumero(conversaSelecionada.numero_telefone)}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="gap-1">
                    <Bot className="h-3 w-3" />
                    VIVA ativa
                  </Badge>
                </div>

                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {mensagens.length === 0 ? (
                      <div className="py-8 text-center text-gray-400">
                        <Bot className="mx-auto mb-4 h-12 w-12" />
                        <p>Nenhuma mensagem ainda</p>
                        <p className="text-sm">A IA VIVA respondera automaticamente</p>
                      </div>
                    ) : (
                      mensagens.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.tipo_origem === "usuario" ? "justify-start" : "justify-end"}`}>
                          <div
                            className={`max-w-[70%] rounded-lg px-4 py-2 ${
                              msg.tipo_origem === "usuario"
                                ? "bg-white text-gray-900 shadow-sm"
                                : msg.tipo_origem === "ia"
                                  ? "bg-blue-500 text-white"
                                  : "bg-gray-200 text-gray-600"
                            }`}
                          >
                            <div className="mb-1 flex items-center gap-2">
                              {msg.tipo_origem === "usuario" ? (
                                <User className="h-3 w-3" />
                              ) : msg.tipo_origem === "ia" ? (
                                <Bot className="h-3 w-3" />
                              ) : null}
                              <span className="text-xs opacity-70">
                                {msg.tipo_origem === "usuario" ? "Cliente" : msg.tipo_origem === "ia" ? "VIVA" : "Sistema"}
                              </span>
                            </div>
                            <p className="whitespace-pre-wrap text-sm">{msg.conteudo}</p>
                            <div className="mt-1 flex items-center justify-end gap-1">
                              <span className="text-xs opacity-60">{formatarData(msg.created_at)}</span>
                              {!msg.enviada && <span className="text-xs text-red-300">x</span>}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>

                <div className="border-t bg-white p-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Digite sua mensagem..."
                      value={novaMensagem}
                      onChange={(e) => setNovaMensagem(e.target.value)}
                      className="flex-1"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleEnviarMensagem();
                        }
                      }}
                    />
                    <Button
                      size="icon"
                      onClick={handleEnviarMensagem}
                      disabled={loadingEnvio || !novaMensagem.trim()}
                      aria-label="Enviar mensagem"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="mt-2 text-center text-xs text-gray-400">
                    Envio manual habilitado. VIVA continua respondendo automaticamente no fluxo webhook.
                  </p>
                </div>
              </>
            ) : (
              <div className="flex flex-1 items-center justify-center text-gray-400">
                <div className="text-center">
                  <MessageCircle className="mx-auto mb-4 h-16 w-16" />
                  <h3 className="text-lg font-medium text-gray-600">Selecione uma conversa</h3>
                  <p className="mt-2">Clique em uma conversa para ver as mensagens</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function WhatsAppConversasPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen bg-gray-100">
          <Sidebar />
          <div className="flex flex-1 items-center justify-center">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        </div>
      }
    >
      <WhatsAppConversasPageContent />
    </Suspense>
  );
}
