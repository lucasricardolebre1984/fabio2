"use client";

import { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { 
  MessageCircle, 
  Archive, 
  RefreshCw, 
  Send,
  Bot,
  User
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

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

export default function WhatsAppConversasPage() {
  const [conversas, setConversas] = useState<Conversa[]>([]);
  const [conversaSelecionada, setConversaSelecionada] = useState<Conversa | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [loading, setLoading] = useState(true);
  const [novaMensagem, setNovaMensagem] = useState("");
  const [stats, setStats] = useState({ conversas_ativas: 0, mensagens_hoje: 0 });
  const { toast } = useToast();

  const carregarConversas = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/whatsapp-chat/conversas", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversas(data);
      }
    } catch (error) {
      console.error("Erro ao carregar conversas:", error);
    }
  }, []);

  const carregarStats = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/whatsapp-chat/status", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Erro ao carregar stats:", error);
    }
  }, []);

  const carregarMensagens = useCallback(async (conversaId: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/whatsapp-chat/conversas/${conversaId}/mensagens`,
        { headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` } }
      );
      
      if (response.ok) {
        const data = await response.json();
        setMensagens(data);
      }
    } catch (error) {
      console.error("Erro ao carregar mensagens:", error);
    }
  }, []);

  useEffect(() => {
    carregarConversas();
    carregarStats();
    setLoading(false);

    const interval = setInterval(() => {
      carregarConversas();
      if (conversaSelecionada) {
        carregarMensagens(conversaSelecionada.id);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [carregarConversas, carregarStats, conversaSelecionada, carregarMensagens]);

  const handleSelecionarConversa = async (conversa: Conversa) => {
    setConversaSelecionada(conversa);
    await carregarMensagens(conversa.id);
  };

  const handleArquivar = async (e: React.MouseEvent, conversaId: string) => {
    e.stopPropagation();
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/whatsapp-chat/conversas/${conversaId}/arquivar`,
        { 
          method: "POST",
          headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
        }
      );
      
      if (response.ok) {
        toast({ title: "Conversa arquivada" });
        carregarConversas();
        if (conversaSelecionada?.id === conversaId) {
          setConversaSelecionada(null);
        }
      }
    } catch (error) {
      toast({ title: "Erro ao arquivar", variant: "destructive" });
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

  if (loading) {
    return (
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <MessageCircle className="h-6 w-6 text-green-500" />
                Conversas WhatsApp
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Atendimento com IA VIVA
              </p>
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

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Lista de Conversas */}
          <div className="w-96 bg-white border-r flex flex-col">
            <div className="p-4 border-b">
              <Input 
                placeholder="Buscar conversa..."
                className="w-full"
              />
            </div>
            
            <ScrollArea className="flex-1">
              {conversas.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhuma conversa ativa</p>
                  <p className="text-sm mt-2">
                    As conversas aparecerão aqui quando clientes enviarem mensagens
                  </p>
                </div>
              ) : (
                <div className="divide-y">
                  {conversas.map((conversa) => (
                    <button
                      key={conversa.id}
                      onClick={() => handleSelecionarConversa(conversa)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                        conversaSelecionada?.id === conversa.id ? "bg-blue-50 border-l-4 border-blue-500" : ""
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="h-10 w-10 bg-blue-100">
                            <AvatarFallback className="text-blue-600 text-sm">
                              {(conversa.nome_contato || conversa.numero_telefone).slice(0, 2).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium text-gray-900">
                              {conversa.nome_contato || formatarNumero(conversa.numero_telefone)}
                            </p>
                            <p className="text-sm text-gray-500">
                              {formatarNumero(conversa.numero_telefone)}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          <span className="text-xs text-gray-400">
                            {formatarData(conversa.ultima_mensagem_em)}
                          </span>
                          <button
                            onClick={(e) => handleArquivar(e, conversa.id)}
                            className="text-gray-400 hover:text-gray-600 p-1"
                            title="Arquivar"
                          >
                            <Archive className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          {/* Área de Chat */}
          <div className="flex-1 flex flex-col bg-gray-50">
            {conversaSelecionada ? (
              <>
                {/* Header do Chat */}
                <div className="bg-white px-6 py-4 border-b flex items-center justify-between">
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
                      <p className="text-sm text-gray-500">
                        {formatarNumero(conversaSelecionada.numero_telefone)}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="gap-1">
                    <Bot className="h-3 w-3" />
                    VIVA ativa
                  </Badge>
                </div>

                {/* Mensagens */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {mensagens.length === 0 ? (
                      <div className="text-center text-gray-400 py-8">
                        <Bot className="h-12 w-12 mx-auto mb-4" />
                        <p>Nenhuma mensagem ainda</p>
                        <p className="text-sm">A IA VIVA responderá automaticamente</p>
                      </div>
                    ) : (
                      mensagens.map((msg) => (
                        <div
                          key={msg.id}
                          className={`flex ${
                            msg.tipo_origem === "usuario" ? "justify-start" : "justify-end"
                          }`}
                        >
                          <div
                            className={`max-w-[70%] rounded-lg px-4 py-2 ${
                              msg.tipo_origem === "usuario"
                                ? "bg-white text-gray-900 shadow-sm"
                                : msg.tipo_origem === "ia"
                                ? "bg-blue-500 text-white"
                                : "bg-gray-200 text-gray-600"
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              {msg.tipo_origem === "usuario" ? (
                                <User className="h-3 w-3" />
                              ) : msg.tipo_origem === "ia" ? (
                                <Bot className="h-3 w-3" />
                              ) : null}
                              <span className="text-xs opacity-70">
                                {msg.tipo_origem === "usuario" ? "Cliente" : msg.tipo_origem === "ia" ? "VIVA" : "Sistema"}
                              </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap">{msg.conteudo}</p>
                            <div className="flex items-center justify-end gap-1 mt-1">
                              <span className="text-xs opacity-60">
                                {formatarData(msg.created_at)}
                              </span>
                              {!msg.enviada && (
                                <span className="text-xs text-red-300">✗</span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </ScrollArea>

                {/* Input */}
                <div className="bg-white p-4 border-t">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Digite sua mensagem..."
                      value={novaMensagem}
                      onChange={(e) => setNovaMensagem(e.target.value)}
                      className="flex-1"
                    />
                    <Button size="icon" disabled>
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 text-center">
                    A IA VIVA está respondendo automaticamente às mensagens
                  </p>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <MessageCircle className="h-16 w-16 mx-auto mb-4" />
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
