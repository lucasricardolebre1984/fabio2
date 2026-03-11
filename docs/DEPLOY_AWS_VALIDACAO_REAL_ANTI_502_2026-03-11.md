# Deploy AWS - Validacao Real Anti-502

Projeto: FC Solucoes Financeiras SaaS  
Data: 2026-03-11  
Objetivo: executar deploy em EC2 com prova real de funcionamento, sem inferencia e sem conflitar owner de porta 80.

## Regra de ouro

Deploy so e considerado concluido quando:

1. `docker compose ... ps` mostra todos os servicos esperados `Up`.
2. `curl` local para upstream real responde:
   - `http://127.0.0.1:3000` (frontend)
   - `http://127.0.0.1:8000/health` (backend)
3. `curl -I https://<dominio>` retorna `200`.
4. Login no frontend e geracao de PDF de contrato funcionam no dominio.

Se qualquer item falhar, deploy nao foi concluido.

## Gate de aceite sem inferencia

Nao encerrar deploy por inferencia de logs ou por "container Up".

Aceite so ocorre com prova real no ambiente AWS onde o SaaS roda:

1. teste HTTP direto no frontend/backend;
2. teste no dominio publico;
3. teste funcional de contratos/PDF no navegador.

## Pre-flight obrigatorio (EC2)

```bash
cd ~/fabio2
git fetch origin
git rev-parse --short HEAD
git rev-parse --short origin/main
```

Esperado: `HEAD == origin/main`.

```bash
if [ -f docker-compose.prod.yml ]; then
  CFILE=docker-compose.prod.yml
else
  CFILE=docker-compose-prod.yml
fi
echo "COMPOSE: $CFILE"
```

### Descobrir owner da porta 80

```bash
sudo ss -ltnp | grep ':80 '
sudo ss -ltnp | grep ':443 ' || true
```

Interpretacao:

1. Se aparecer `nginx` do host Ubuntu, **nao** subir compose nginx em `80:80`.
2. Se nao houver owner em `:80`, compose pode assumir `80:80`.

## Estrategias validas (escolher uma)

### Estrategia A (recomendada)

Host nginx faz TLS em `:80/:443`, compose nginx escuta somente loopback `127.0.0.1:8088:80`.

```bash
grep -nA8 '^  nginx:' "$CFILE"
```

Garantir mapeamento:

```yaml
ports:
  - "127.0.0.1:8088:80"
```

### Estrategia B

Compose nginx eh owner unico da `:80` e host nginx do Ubuntu esta parado/desativado.

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
```

## Deploy real (com validação)

```bash
cd ~/fabio2
docker compose -f "$CFILE" up -d --build --remove-orphans
docker compose -f "$CFILE" ps
docker compose -f "$CFILE" logs --tail=120 backend
docker compose -f "$CFILE" logs --tail=120 frontend
docker compose -f "$CFILE" logs --tail=120 nginx
```

## Smoke local na EC2

### Quando frontend/backend nao publicam portas no host

```bash
docker exec fabio2-frontend wget -qSO- http://127.0.0.1:3000 2>&1 | head
docker exec fabio2-backend wget -qSO- http://127.0.0.1:8000/health 2>&1 | head
```

### Quando compose nginx usa `127.0.0.1:8088:80`

```bash
curl -I http://127.0.0.1:8088
```

### Dominio final

```bash
curl -I https://fabio.automaniaai.com.br
```

Esperado: `HTTP/1.1 200`.

## Validacao funcional obrigatoria (dominio)

1. Fazer login.
2. Abrir modulo Contratos.
3. Gerar PDF de um contrato comum (ex.: `bacen`) e confirmar 1 anexo.
4. Gerar PDF de um contrato de rating (`aumento_score`/`rating_*`) e confirmar 2 anexos.
5. Confirmar preenchimento de cabecalho dos anexos (numero, data, nome, CPF/CNPJ).

## Diagnostico rapido de 502

Se ocorrer 502, rodar:

```bash
docker compose -f "$CFILE" ps
docker compose -f "$CFILE" logs --tail=200 nginx
docker compose -f "$CFILE" logs --tail=200 frontend
docker compose -f "$CFILE" logs --tail=200 backend
sudo ss -ltnp | grep ':80 '
```

Assinaturas conhecidas:

1. `connect() failed (111: Connection refused) ... upstream ...:3000`:
   - frontend indisponivel ou nginx container nao conectado.
2. `failed to bind host port 0.0.0.0:80`:
   - conflito de owner da porta 80 (host nginx x compose nginx).

## Evidencias minimas obrigatorias (anexar no fechamento)

Salvar no ticket/registro:

1. `git rev-parse --short HEAD`
2. `docker compose -f "$CFILE" ps`
3. `curl -I http://127.0.0.1:8088` (quando estrategia A)
4. `curl -I https://fabio.automaniaai.com.br`
5. screenshot de:
   - login concluido;
   - contrato comum com 1 anexo;
   - contrato rating com 2 anexos.

## Rollback de emergencia

```bash
cd ~/fabio2
git log --oneline -n 5
git reset --hard <commit_anterior_estavel>
docker compose -f "$CFILE" up -d --build --remove-orphans
```

Observacao: usar rollback por patch COFRE quando a rodada tiver patch institucional dedicado.
