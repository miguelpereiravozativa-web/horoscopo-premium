# AuraDex Premium - Integração Mercado Pago

Aplicação Streamlit com sistema de pagamento integrado via Mercado Pago. Fluxo completo: teste comportamental → gerar arquétipo → pagamento R$ 1,99 → desbloquear PDF premium.

## 🎯 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│ Streamlit App (Frontend)                                    │
│ - Teste comportamental (12 perguntas)                       │
│ - Resultado gratuito (perfil básico)                        │
│ - Tela de pagamento (link Mercado Pago)                     │
│ - Relatório premium (após pagamento aprovado)               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ API Calls
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Backend (backend.py)                                │
│ - POST /create-payment → Criar preferência MP               │
│ - POST /api/webhook → Receber webhook do MP                 │
│ - GET /check-payment/{email} → Status do pagamento          │
│ - POST /unlock-report/{email} → Desbloquear relatório       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Database Operations
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ SQLite Database (payments.db)                               │
│ - Tabela: payments (email, status, MP_ID, ...)             │
│ - Tabela: unlock_tokens (token, expires_at, ...)           │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Estrutura de Arquivos

```
horoscopo-premium/
├── main.py                    # App Streamlit (frontend)
├── backend.py                 # FastAPI backend com webhooks
├── database.py                # Gerenciamento SQLite
├── mercado_pago_utils.py      # Utilitários de integração
├── requirements.txt           # Dependências Python
├── payments.db                # SQLite database (gerado)
├── .streamlit/
│   ├── config.toml           # Config Streamlit
│   └── secrets.toml          # Credenciais MP (NÃO commitar)
└── README.md                 # Este arquivo
```

## 🚀 Setup Local

### Pré-requisitos

- Python 3.9+
- Conta Mercado Pago (produção ou sandbox)
- pip/virtualenv

### 1. Clonar e instalar dependências

```bash
cd horoscopo-premium
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar credenciais Mercado Pago

1. Ir para: https://www.mercadopago.com.br/developers/panel
2. Criar aplicação (ou usar existente)
3. Copiar **Access Token**
4. Copiar **User ID**
5. Editar `.streamlit/secrets.toml`:

```toml
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-1234567890123456789012345678901234567890"
MERCADO_PAGO_USER_ID = "123456789"
WEBHOOK_SECRET = "seu_webhook_secret_seguro_aqui"
BACKEND_URL = "http://localhost:8000"
BASE_URL = "http://localhost:8501"
```

### 3. Executar backend localmente

```bash
# Terminal 1: Backend FastAPI
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
# API disponível em: http://localhost:8000/docs
```

### 4. Executar Streamlit

```bash
# Terminal 2: Streamlit App
streamlit run main.py
# App disponível em: http://localhost:8501
```

## 🌐 Deploy no Streamlit Community Cloud

### Passo 1: Push para GitHub

```bash
git add .
git commit -m "Add Mercado Pago integration"
git push origin main
```

**⚠️ IMPORTANTE:** Adicione `.streamlit/secrets.toml` ao `.gitignore`
```bash
echo ".streamlit/secrets.toml" >> .gitignore
git add .gitignore
git commit -m "Add secrets to gitignore"
```

### Passo 2: Configurar em Streamlit Cloud

1. Ir para: https://share.streamlit.io
2. Conectar GitHub
3. Selecionar repositório `horoscopo-premium`
4. Clicar em "Advanced settings"
5. Adicionar secrets:

```toml
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-..."
MERCADO_PAGO_USER_ID = "123456789"
WEBHOOK_SECRET = "seu_secret"
BACKEND_URL = "https://seu-backend.com"
BASE_URL = "https://seu-app.streamlit.app"
```

## 🔧 Deploy Backend (opções)

### Opção A: Heroku (RECOMENDADO para inicio)

1. Instalar Heroku CLI
2. Criar app:
```bash
heroku login
heroku create seu-app-backend
```

3. Criar `Procfile`:
```
web: uvicorn backend:app --host 0.0.0.0 --port $PORT
```

4. Configurar variáveis ambiente:
```bash
heroku config:set MERCADO_PAGO_ACCESS_TOKEN="APP_USR-..."
heroku config:set MERCADO_PAGO_USER_ID="123456789"
heroku config:set WEBHOOK_SECRET="seu_secret"
heroku config:set BASE_URL="https://seu-app.streamlit.app"
```

5. Deploy:
```bash
git push heroku main
```

6. Atualizar `BACKEND_URL` em Streamlit Cloud:
```
BACKEND_URL = "https://seu-app-backend.herokuapp.com"
```

### Opção B: Railway

1. Conectar GitHub em https://railway.app
2. Selecionar repo
3. Adicionar variáveis de ambiente
4. Deploy automático
5. Copiar URL do backend para Streamlit

### Opção C: Render

1. Conectar GitHub em https://render.com
2. Criar novo Web Service
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend:app --host 0.0.0.0 --port 8000`
5. Adicionar environment variables
6. Deploy

## 🪝 Webhook do Mercado Pago

### Configurar notificações

1. Ir para: https://www.mercadopago.com.br/developers/panel/notifications
2. Tipo: **Webhooks**
3. URL: `https://seu-backend.com/api/webhook`
4. Eventos: 
   - ✅ payment.created
   - ✅ payment.updated
   - ✅ merchant_order.updated

### Testar webhook localmente

```bash
# Terminal 3: Expor localhost para webhooks
# Instalar ngrok: https://ngrok.com

ngrok http 8000
# Copia a URL: https://xxx.ngrok.io

# Atualizar secrets.toml
BASE_URL = "https://xxx.ngrok.io"
```

## 💳 Fluxo de Pagamento

### 1. Usuário inicia pagamento
- Clica em "🚀 LIBERAR ACESSO EXECUTIVO"
- API cria preferência no Mercado Pago
- Usuário é redirecionado para checkout

### 2. Pagamento aprovado
- Mercado Pago envia webhook
- Backend atualiza status em SQLite → `approved`
- Usuário volta para Streamlit
- App detecta pagamento aprovado
- Relatório premium é desbloqueado ✓

### 3. Acesso ao PDF
- Usuário pode fazer download do PDF de 5 páginas
- Token de desbloqueio válido por 30 dias

## 🔐 Segurança

- ✅ Access Token armazenado em `secrets.toml`
- ✅ Webhook Secret para validar requisições MP
- ✅ Tokens de desbloqueio com expiração
- ✅ CORS configurado no backend
- ✅ Validações no banco antes de desbloquear

## 📊 Monitoramento

### Ver status de pagamentos

```python
# Terminal: consultar banco
from database import Database
db = Database()
stats = db.get_payment_stats()
for stat in stats:
    print(f"{stat['status']}: {stat['count']} pagamentos, R$ {stat['total']}")
```

### Logs do backend

```bash
# Verificar logs Heroku
heroku logs --tail

# Ou Railway/Render dashboard
```

## 🧪 Testes

### Teste com Sandbox do MP

1. Em Mercado Pago settings, usar **modo sandbox**
2. Usar cartões de teste:
   - Visa: 4111 1111 1111 1111 (Any future date, any CVV)
   - Mastercard: 5555 4444 3333 1111
   - 04/2025 / 123

### Validar fluxo completo

1. Abrir app no navegador
2. Completar teste (12 perguntas)
3. Ver resultado gratuito
4. Clicar em "🚀 LIBERAR ACESSO EXECUTIVO"
5. Preencher email
6. Ir para checkout
7. Pagar com cartão de teste
8. Voltar e verificar "Já paguei?"
9. Relatório premium deve aparecer
10. Download PDF ✓

## ⚙️ Configurações Avançadas

### Ajustar preço do produto

Editar `backend.py`:
```python
PRODUCT_PRICE = 9.99  # Mudar aqui
PRODUCT_TITLE = "Novo título..."
```

### Customizar email de confirmação

Adicionar ao `backend.py`:
```python
import smtplib
from email.mime.text import MIMEText

def send_confirmation_email(user_email, user_name):
    # Implementar envio de email
    pass
```

### Adicionar mais produtos

Criar tabela no `database.py`:
```python
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    ...
)
```

## 📝 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `MERCADO_PAGO_ACCESS_TOKEN` | Token da API MP | `APP_USR-xxx` |
| `MERCADO_PAGO_USER_ID` | ID do usuário MP | `123456789` |
| `WEBHOOK_SECRET` | Secret para validar webhooks | `seg_123_abc` |
| `BACKEND_URL` | URL do backend | `https://backend.com` |
| `BASE_URL` | URL do frontend Streamlit | `https://app.streamlit.app` |
| `DATABASE_PATH` | Caminho do SQLite | `payments.db` |

## 🐛 Troubleshooting

### "Erro ao criar preferência de pagamento"
- Verificar `MERCADO_PAGO_ACCESS_TOKEN` em secrets.toml
- Confirmar que o token começa com `APP_USR-`
- Verificar modo (sandbox vs produção)

### "Webhook não está sendo recebido"
- Validar URL em Mercado Pago dashboard
- Usar ngrok para testar localmente
- Verificar logs do backend: `heroku logs --tail`

### "Token de desbloqueio expirado"
- Tokens válidos por 30 dias
- Criar novo token via `/unlock-report/{email}`

### App trava ao carregar relatório
- Verificar SQLite não está locked: `rm payments.db`
- Aumentar timeout: editar `mercado_pago_utils.py` timeout=60

## 📞 Suporte Mercado Pago

- Docs: https://www.mercadopago.com.br/developers/pt/docs
- Comunidade: https://forum.mercadopago.com
- Status API: https://status.mercadopago.com

## 📄 Licença

Este projeto é privado. Não distribuir sem permissão.

---

**Última atualização:** 2026-06-18
**Versão:** 1.0.0
