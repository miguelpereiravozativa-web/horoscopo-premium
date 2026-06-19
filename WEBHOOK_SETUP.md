# Configuração de Webhook - Mercado Pago

## 📡 Como configurar notificações do Mercado Pago

### Passo 1: Acessar o dashboard

1. Ir para: https://www.mercadopago.com.br/developers/panel
2. Selecionar sua aplicação
3. Menu lateral → **Webhooks** (ou **Notificações**)

### Passo 2: Adicionar URL do webhook

**URL:** `https://seu-backend.com/api/webhook`

Exemplos:
- Heroku: `https://seu-app-backend.herokuapp.com/api/webhook`
- Railway: `https://seu-app.railway.app/api/webhook`
- Render: `https://seu-app.onrender.com/api/webhook`

### Passo 3: Selecionar eventos

Ativar os seguintes eventos:

```
✅ payment.created
✅ payment.updated
✅ merchant_order.updated
```

### Passo 4: Testar webhook localmente

Para testar a integração antes de fazer deploy:

#### Opção A: Usar ngrok (RECOMENDADO)

1. Baixar: https://ngrok.com/download
2. Extrair e adicionar ao PATH
3. Em terminal novo:
```bash
ngrok http 8000
```

4. Copiar URL gerada (ex: `https://abc123.ngrok.io`)

5. Editar `.streamlit/secrets.toml`:
```toml
BASE_URL = "https://abc123.ngrok.io"
```

6. Adicionar webhook em MP:
```
https://abc123.ngrok.io/api/webhook
```

7. Testar pagamento no sandbox

#### Opção B: Usar localtunnel

```bash
npm install -g localtunnel
lt --port 8000
# Copiar URL e adicionar a /api/webhook
```

### Passo 5: Validar recebimento

#### Logs do Mercado Pago

1. No dashboard, ir para **Webhooks** → **Histórico de eventos**
2. Ver tentativas de envio
3. Status 200 = sucesso ✅

#### Logs do backend

```bash
# Heroku
heroku logs --tail

# Railway/Render - via dashboard
```

#### Verificar banco de dados

```python
from database import Database

db = Database()
payments = db.get_payment_stats()
for p in payments:
    print(f"{p['status']}: {p['count']}")
```

---

## 🔐 Segurança do Webhook

### Validar requisições

O webhook NÃO valida assinatura por padrão. Para adicionar validação:

```python
# backend.py - adicionar assinatura MP

import hmac
import hashlib

def verify_mp_signature(request_body: str, signature: str, secret: str) -> bool:
    """Validar assinatura do Mercado Pago"""
    calculated = hmac.new(
        secret.encode(),
        request_body.encode(),
        hashlib.sha256
    ).hexdigest()
    return calculated == signature

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    body = await request.body()
    signature = request.headers.get("x-signature", "")
    
    if not verify_mp_signature(body.decode(), signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Processar webhook...
```

### Rate limiting

Para evitar abuso:

```python
from slowapi import Limiter

limiter = Limiter(key_func=...)
app.state.limiter = limiter

@app.post("/api/webhook")
@limiter.limit("100/minute")
async def webhook_handler(request: Request):
    # ...
```

---

## 🧪 Payloads de Teste

### Pagamento aprovado

```json
{
  "topic": "payment",
  "resource": {
    "id": "12345678901"
  }
}
```

### Pedido atualizado

```json
{
  "topic": "merchant_order",
  "resource": {
    "id": "9876543210"
  }
}
```

### Simular no terminal

```bash
# Enviar webhook de teste
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "payment",
    "resource": {"id": "12345678901"}
  }'
```

---

## 📋 Checklist de Deploy

- [ ] Backend em produção (Heroku/Railway/Render)
- [ ] Webhook URL configurada em MP Dashboard
- [ ] Eventos selecionados (payment.created, payment.updated)
- [ ] WEBHOOK_SECRET configurado em production env
- [ ] BASE_URL aponta para domínio correto
- [ ] Testar pagamento completo
- [ ] Verificar emails de confirmação (se implementado)
- [ ] Logs sendo gerados corretamente
- [ ] SQLite ou banco externo configurado
- [ ] CORS habilitado para Streamlit Cloud URL

---

## 🚨 Troubleshooting

### Webhook não está sendo enviado

1. Verificar URL em MP Dashboard
2. Confirmar que backend está online
3. Testar health check:
```bash
curl https://seu-backend.com/health
```

### Pagamento não aparece no banco

1. Verificar logs do backend: `heroku logs --tail`
2. Confirmar status em MP Dashboard
3. Se webhook chegou mas erro ocorreu:
   - Verificar banco SQLite está accessible
   - Confirmar tabelas foram criadas: `python database.py`

### Muitos erros 500 no histórico

1. Verificar se backend está online
2. Ver logs para error stacktrace
3. Possível causa:
   - Token MP expirado
   - Banco de dados locked
   - Variável de ambiente não configurada

### Webhook continua falhando

1. Regenerar WEBHOOK_SECRET
2. Remover webhook antigo
3. Adicionar novo webhook
4. Testar com ngrok primeiro

---

## 📞 Suporte Mercado Pago

- **Status API:** https://status.mercadopago.com
- **Fórum:** https://forum.mercadopago.com
- **Documentação:** https://www.mercadopago.com.br/developers/pt/docs
- **Email:** developers@mercadopago.com

---

**Última atualização:** 2026-06-18
