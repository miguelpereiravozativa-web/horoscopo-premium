# 🚀 GUIA RÁPIDO - MERCADO PAGO + STREAMLIT

## ⚡ Setup em 10 minutos

### 1️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Obter credenciais Mercado Pago

1. Acessar: https://www.mercadopago.com.br/developers/panel
2. Criar aplicação
3. Copiar **Access Token** (começar com `APP_USR-`)
4. Copiar **User ID**

### 3️⃣ Configurar secrets.toml

Editar `.streamlit/secrets.toml`:

```toml
MERCADO_PAGO_ACCESS_TOKEN = "APP_USR-seu_token_aqui"
MERCADO_PAGO_USER_ID = "seu_user_id"
WEBHOOK_SECRET = "seu_secret_aleatorio"
BACKEND_URL = "http://localhost:8000"
BASE_URL = "http://localhost:8501"
```

### 4️⃣ Rodar Backend (Terminal 1)

```bash
python -m uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

Ver em: http://localhost:8000/docs (swagger docs)

### 5️⃣ Rodar Streamlit (Terminal 2)

```bash
streamlit run main.py
```

Abrirá em: http://localhost:8501

### 6️⃣ Testar o fluxo completo

1. Completar 12 perguntas
2. Ver resultado gratuito
3. Clicar "🚀 LIBERAR ACESSO EXECUTIVO"
4. Preencher email
5. Ir para checkout (sandbox)
6. Pagar com: `4111 1111 1111 1111` / `04/25` / `123`
7. Relatório deve aparecer ✅

---

## 📦 Arquivos criados/modificados

| Arquivo | Descrição |
|---------|-----------|
| `backend.py` | **NOVO** - FastAPI com webhooks MP |
| `database.py` | **NOVO** - SQLite para pagamentos |
| `mercado_pago_utils.py` | **NOVO** - Integração MP + Streamlit |
| `main.py` | **MODIFICADO** - Adicionado fluxo de pagamento |
| `requirements.txt` | **NOVO** - Dependências |
| `.streamlit/secrets.toml` | **NOVO** - Credenciais (NÃO commitar) |
| `.streamlit/config.toml` | **NOVO** - Config Streamlit |
| `Procfile` | **NOVO** - Deploy Heroku |
| `test_integration.py` | **NOVO** - Testes de integração |
| `.gitignore` | **NOVO** - Arquivos para ignorar |

---

## 🔑 Variáveis de Ambiente Obrigatórias

```bash
MERCADO_PAGO_ACCESS_TOKEN    # Token da API Mercado Pago
MERCADO_PAGO_USER_ID         # ID do usuário MP
WEBHOOK_SECRET               # Secret para webhooks (pode ser qualquer string)
BACKEND_URL                  # URL do backend (localhost ou produção)
BASE_URL                     # URL do Streamlit (localhost ou Streamlit Cloud)
```

---

## 🚀 Deploy em Produção

### Opção 1: Streamlit Cloud (Frontend) + Heroku (Backend)

**Frontend:**
1. Push para GitHub
2. Conectar em https://share.streamlit.io
3. Adicionar secrets (menu settings)

**Backend:**
```bash
heroku login
heroku create seu-app-backend
git push heroku main
heroku config:set MERCADO_PAGO_ACCESS_TOKEN="..."
```

### Opção 2: Railway ou Render (Full Stack)

1. Conectar GitHub
2. Criar dois serviços:
   - Backend: `uvicorn backend:app --host 0.0.0.0 --port 8000`
   - Frontend: `streamlit run main.py --server.port 8501`
3. Adicionar environment variables

---

## 🧪 Testar Integração

```bash
python test_integration.py
```

Testa:
- ✅ Health check do backend
- ✅ Criar preferência de pagamento
- ✅ Verificar status de pagamento
- ✅ Desbloquear relatório
- ✅ Validar tokens
- ✅ Operações de banco de dados

---

## 📊 Fluxo de Pagamento

```
Usuário inicia pagamento
    ↓
API cria preferência MP
    ↓
Redirect para checkout
    ↓
Pagamento aprovado/rejeitado
    ↓
MP envia webhook
    ↓
Backend atualiza SQLite
    ↓
Streamlit detecta pagamento
    ↓
Relatório desbloqueado ✅
```

---

## 🔒 Segurança

- ✅ Tokens em `.streamlit/secrets.toml` (NÃO commitar)
- ✅ Webhooks validados com secret
- ✅ CORS configurado
- ✅ Tokens de desbloqueio com expiração 30 dias
- ✅ SQLite com lock para operações concorrentes

---

## 📞 Problemas Comuns

### "Backend não está respondendo"
```bash
# Verificar se está rodando
python -m uvicorn backend:app --reload
```

### "Token MP inválido"
- Confirmar token começa com `APP_USR-`
- Verificar ambiente (sandbox vs produção)
- Regenerar em: https://www.mercadopago.com.br/developers/panel

### "Webhook não é recebido"
- Validar URL em MP dashboard
- Para testar local, usar ngrok:
```bash
ngrok http 8000
# Copiar URL e adicionar /api/webhook
```

### "Payment locked" erro no SQLite
- Remover `payments.db`
- Recriar: `python database.py`

---

## 📚 Recursos

- Docs MP: https://www.mercadopago.com.br/developers/pt
- Streamlit: https://docs.streamlit.io
- FastAPI: https://fastapi.tiangolo.com
- SQLite: https://www.sqlite.org/docs.html

---

**Próximas melhorias:**
- [ ] Email de confirmação após pagamento
- [ ] Dashboard de admin com estatísticas
- [ ] Suporte a múltiplos produtos/preços
- [ ] Sistema de afiliados/comissão
- [ ] API de relatórios

---

**Suporte:** verificar `README_MERCADO_PAGO.md` para docs completas
