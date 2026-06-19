"""
FastAPI Backend para Mercado Pago Webhook Integration
Gerencia pagamentos, webhooks e status de desbloqueio
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
from datetime import datetime
from database import Database

app = FastAPI(title="AuraDex Payment Backend", version="1.0.0")

# CORS configuração para Streamlit Community Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados
db = Database()
db.init_db()

# Configurações do Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
MERCADO_PAGO_USER_ID = os.getenv("MERCADO_PAGO_USER_ID", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "seu_webhook_secret_aqui")

PRODUCT_PRICE = 1.99
PRODUCT_TITLE = "Relatório Executivo Premium - AuraDex Arquétipos"
PRODUCT_DESCRIPTION = "Dossiê Completo de 5 Páginas com Análise Comportamental Premium"

# Base URL - ajustar conforme o deploy
BASE_URL = os.getenv("BASE_URL", "https://seu-app.streamlit.app")


@app.get("/health")
def health_check():
    """Verificar saúde da API"""
    return {"status": "ok", "service": "AuraDex Payment Backend"}


@app.post("/create-payment")
async def create_payment(user_email: str, user_name: str):
    """
    Criar preferência de pagamento no Mercado Pago
    Retorna a URL de checkout
    """
    if not MERCADO_PAGO_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Mercado Pago token não configurado")

    preference_data = {
        "items": [
            {
                "title": PRODUCT_TITLE,
                "description": PRODUCT_DESCRIPTION,
                "unit_price": PRODUCT_PRICE,
                "quantity": 1,
                "currency_id": "BRL",
            }
        ],
        "payer": {
            "email": user_email,
            "name": user_name,
        },
        "back_urls": {
            "success": f"{BASE_URL}?payment_status=approved",
            "failure": f"{BASE_URL}?payment_status=pending",
            "pending": f"{BASE_URL}?payment_status=pending",
        },
        "auto_return": "approved",
        "notification_url": f"{BASE_URL}/api/webhook",
        "external_reference": user_email,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.mercadopago.com/checkout/preferences",
            json=preference_data,
            headers=headers,
        )

        if response.status_code != 201:
            raise HTTPException(
                status_code=400, detail="Falha ao criar preferência de pagamento"
            )

        preference = response.json()
        preference_id = preference.get("id")

        # Salvar no banco que o pagamento foi iniciado
        db.save_payment(
            user_email=user_email,
            user_name=user_name,
            preference_id=preference_id,
            status="pending",
            amount=PRODUCT_PRICE,
        )

        return {
            "init_point": preference.get("init_point"),
            "preference_id": preference_id,
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }


@app.post("/api/webhook")
async def webhook_handler(request: Request):
    """
    Receber webhooks do Mercado Pago
    Atualizar status de pagamento no banco
    """
    try:
        body = await request.json()

        # Extrair dados do webhook
        topic = body.get("topic")  # payment ou merchant_order
        resource_id = body.get("resource").get("id") if body.get("resource") else None

        if not resource_id:
            return {"status": "received"}

        # Se é um pagamento
        if topic == "payment":
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.mercadopago.com/v1/payments/{resource_id}",
                    headers={
                        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
                    },
                )

                if response.status_code == 200:
                    payment_data = response.json()
                    external_reference = payment_data.get("external_reference")
                    status = payment_data.get("status")
                    payment_method = payment_data.get("payment_method_id", "unknown")

                    # Mapear status do Mercado Pago
                    if status in ["approved"]:
                        db_status = "approved"
                    elif status in ["pending", "in_process"]:
                        db_status = "pending"
                    elif status in ["rejected", "cancelled", "refunded"]:
                        db_status = "failed"
                    else:
                        db_status = "unknown"

                    # Atualizar banco
                    db.update_payment_status(
                        user_email=external_reference,
                        status=db_status,
                        mercado_pago_id=resource_id,
                        payment_method=payment_method,
                    )

        return {"status": "received"}

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return {"status": "received"}


@app.get("/check-payment/{user_email}")
def check_payment_status(user_email: str):
    """
    Verificar status de pagamento do usuário
    Retorna: approved, pending, failed, ou not_found
    """
    payment = db.get_payment_by_email(user_email)

    if not payment:
        return {"status": "not_found", "user_email": user_email}

    return {
        "status": payment["status"],
        "user_email": user_email,
        "created_at": payment["created_at"],
        "amount": payment["amount"],
    }


@app.post("/unlock-report/{user_email}")
def unlock_report(user_email: str):
    """
    Endpoint para desbloquear o relatório após pagamento
    Verifica se o pagamento foi aprovado
    """
    payment = db.get_payment_by_email(user_email)

    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")

    if payment["status"] != "approved":
        raise HTTPException(status_code=403, detail="Pagamento não foi aprovado")

    # Gerar token/session de desbloqueio
    unlock_token = db.create_unlock_token(user_email)

    return {
        "unlocked": True,
        "token": unlock_token,
        "message": "Relatório desbloqueado com sucesso!",
    }


@app.get("/verify-token/{token}")
def verify_unlock_token(token: str):
    """
    Verificar se um token de desbloqueio é válido
    """
    is_valid = db.verify_unlock_token(token)
    return {"valid": is_valid}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
