"""
Utilities para integração Mercado Pago com Streamlit
"""

import streamlit as st
import httpx
import os
from urllib.parse import urlencode

# Configurações
BACKEND_URL = os.getenv("BACKEND_URL", "https://seu-backend.com")


class MercadoPagoManager:
    def __init__(self, backend_url=BACKEND_URL):
        self.backend_url = backend_url.rstrip("/")

    async def create_payment_preference(self, user_email: str, user_name: str):
        """
        Criar preferência de pagamento via backend
        Retorna URL de checkout
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/create-payment",
                    params={
                        "user_email": user_email,
                        "user_name": user_name,
                    },
                    timeout=30,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except Exception as e:
            st.error(f"Erro ao criar preferência de pagamento: {str(e)}")
            return None

    def check_payment_status(self, user_email: str):
        """
        Verificar status de pagamento
        Retorna: approved, pending, failed, not_found
        """
        try:
            response = httpx.get(
                f"{self.backend_url}/check-payment/{user_email}",
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error"}
        except Exception as e:
            st.error(f"Erro ao verificar pagamento: {str(e)}")
            return {"status": "error"}

    def unlock_report(self, user_email: str):
        """
        Desbloquear relatório após pagamento aprovado
        Retorna token de desbloqueio
        """
        try:
            response = httpx.post(
                f"{self.backend_url}/unlock-report/{user_email}",
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"unlocked": False}
        except Exception as e:
            st.error(f"Erro ao desbloquear relatório: {str(e)}")
            return {"unlocked": False}

    def verify_token(self, token: str):
        """
        Verificar se token de desbloqueio é válido
        """
        try:
            response = httpx.get(
                f"{self.backend_url}/verify-token/{token}",
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"valid": False}
        except Exception as e:
            return {"valid": False}


def render_payment_button(user_email: str, user_name: str):
    """
    Renderizar botão de pagamento integrado
    Abre link de checkout do Mercado Pago
    """
    mp = MercadoPagoManager()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 LIBERAR ACESSO EXECUTIVO", use_container_width=True):
            with st.spinner("Preparando link de pagamento..."):
                import asyncio

                payment_data = asyncio.run(mp.create_payment_preference(user_email, user_name))

                if payment_data and payment_data.get("init_point"):
                    st.session_state.checkout_url = payment_data["init_point"]
                    st.session_state.payment_preference_id = payment_data.get("preference_id")
                    st.rerun()

    with col2:
        if st.button("✓ Já paguei - Verificar Status", use_container_width=True):
            with st.spinner("Verificando status de pagamento..."):
                status_data = mp.check_payment_status(user_email)

                if status_data["status"] == "approved":
                    st.success("✓ Pagamento aprovado! Desbloqueando acesso...")
                    st.session_state.payment_approved = True
                    st.rerun()
                elif status_data["status"] == "pending":
                    st.warning("⏳ Pagamento ainda está sendo processado. Tente novamente em alguns minutos.")
                elif status_data["status"] == "failed":
                    st.error("✗ Pagamento foi rejeitado. Tente novamente.")
                else:
                    st.info("ℹ️ Nenhum pagamento encontrado para este email.")


def render_checkout_redirect(checkout_url: str):
    """
    Renderizar redirecionamento para checkout
    """
    st.markdown(f"""
        <div style='text-align:center; margin: 2rem 0;'>
            <p style='font-size:1.1rem; color:#e4e6eb; margin-bottom:1.5rem;'>
                Você será redirecionado para o checkout seguro do Mercado Pago em 3 segundos...
            </p>
            <a href="{checkout_url}" target="_blank" style='
                display:inline-block;
                background: linear-gradient(135deg, #b8860b 0%, #e6ca65 50%, #996515 100%);
                color: #0d1117;
                font-weight: bold;
                font-size:1.05rem;
                letter-spacing: 2px;
                padding: 14px 30px;
                border-radius: 6px;
                text-decoration: none;
                text-transform: uppercase;
                box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
            '>
                🔐 Ir para Checkout Seguro
            </a>
        </div>
        <script>
            setTimeout(function() {{
                window.open("{checkout_url}", "_blank");
            }}, 3000);
        </script>
    """, unsafe_allow_html=True)


def check_payment_and_unlock(user_email: str):
    """
    Verificar URL param de status e desbloquear se aprovado
    Usar na tela premium_report ou similar
    """
    from urllib.parse import urlparse, parse_qs

    query_params = st.query_params

    if "payment_status" in query_params:
        status = query_params["payment_status"]

        if status == "approved":
            mp = MercadoPagoManager()

            with st.spinner("Verificando pagamento..."):
                payment_data = mp.check_payment_status(user_email)

                if payment_data["status"] == "approved":
                    unlock_data = mp.unlock_report(user_email)

                    if unlock_data.get("unlocked"):
                        st.session_state.payment_approved = True
                        st.session_state.unlock_token = unlock_data.get("token")
                        st.success("✓ Acesso desbloqueado com sucesso!")
                        return True

    return st.session_state.get("payment_approved", False)
