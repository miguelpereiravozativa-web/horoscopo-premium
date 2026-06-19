"""
Script de teste para validar integração Mercado Pago
Execute: python test_integration.py
"""

import os
import asyncio
import httpx
from database import Database

# Configurar variáveis de teste
TEST_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TEST_USER_EMAIL = "teste@example.com"
TEST_USER_NAME = "Teste User"

db = Database()
db.init_db()


async def test_payment_creation():
    """Teste: Criar preferência de pagamento"""
    print("\n🧪 TESTE 1: Criar preferência de pagamento")
    print("-" * 50)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TEST_BACKEND_URL}/create-payment",
                params={
                    "user_email": TEST_USER_EMAIL,
                    "user_name": TEST_USER_NAME,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ SUCESSO: Preferência criada")
                print(f"   Preference ID: {data.get('preference_id')}")
                print(f"   Checkout URL: {data.get('init_point', 'N/A')[:80]}...")
                return data.get("preference_id")
            else:
                print(f"❌ ERRO: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            return None


async def test_payment_status(user_email: str):
    """Teste: Verificar status de pagamento"""
    print("\n🧪 TESTE 2: Verificar status de pagamento")
    print("-" * 50)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TEST_BACKEND_URL}/check-payment/{user_email}",
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print("✅ SUCESSO: Status obtido")
                print(f"   Email: {data.get('user_email')}")
                print(f"   Status: {status}")
                print(f"   Criado em: {data.get('created_at')}")
                return status
            elif response.status_code == 404:
                print("✅ ESPERADO: Pagamento não encontrado (novo usuário)")
                return "not_found"
            else:
                print(f"❌ ERRO: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            return None


async def test_unlock_report(user_email: str):
    """Teste: Desbloquear relatório (requer pagamento aprovado)"""
    print("\n🧪 TESTE 3: Desbloquear relatório")
    print("-" * 50)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TEST_BACKEND_URL}/unlock-report/{user_email}",
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ SUCESSO: Relatório desbloqueado")
                print(f"   Token: {data.get('token', 'N/A')[:20]}...")
                print(f"   Mensagem: {data.get('message')}")
                return data.get("token")
            elif response.status_code == 403:
                print("⚠️  ESPERADO: Pagamento não foi aprovado (status pending/failed)")
                return None
            elif response.status_code == 404:
                print("⚠️  ESPERADO: Pagamento não encontrado")
                return None
            else:
                print(f"❌ ERRO: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            return None


async def test_verify_token(token: str):
    """Teste: Verificar token de desbloqueio"""
    print("\n🧪 TESTE 4: Verificar token de desbloqueio")
    print("-" * 50)

    if not token:
        print("⏭️  PULADO: Nenhum token disponível")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{TEST_BACKEND_URL}/verify-token/{token}",
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                valid = data.get("valid")
                if valid:
                    print("✅ SUCESSO: Token é válido")
                else:
                    print("⚠️  Token inválido ou expirado")
                return valid
            else:
                print(f"❌ ERRO: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            return False


def test_database():
    """Teste: Operações de banco de dados"""
    print("\n🧪 TESTE 5: Operações de banco de dados")
    print("-" * 50)

    try:
        # Salvar pagamento
        db.save_payment(
            user_email=TEST_USER_EMAIL,
            user_name=TEST_USER_NAME,
            preference_id="MP-12345",
            status="pending",
            amount=1.99,
        )
        print("✅ Pagamento salvo no banco")

        # Obter pagamento
        payment = db.get_payment_by_email(TEST_USER_EMAIL)
        if payment:
            print(f"✅ Pagamento recuperado: {payment['status']}")
        else:
            print("❌ Falha ao recuperar pagamento")

        # Atualizar status
        db.update_payment_status(
            user_email=TEST_USER_EMAIL,
            status="approved",
            mercado_pago_id="MP-999",
            payment_method="credit_card",
        )
        print("✅ Status atualizado para 'approved'")

        # Criar token
        token = db.create_unlock_token(TEST_USER_EMAIL)
        print(f"✅ Token criado: {token[:20]}...")

        # Verificar token
        valid = db.verify_unlock_token(token)
        if valid:
            print("✅ Token verificado como válido")
        else:
            print("❌ Token inválido")

        # Stats
        stats = db.get_payment_stats()
        print("✅ Estatísticas de pagamentos:")
        for stat in stats:
            print(f"   {stat['status']}: {stat['count']} registros")

    except Exception as e:
        print(f"❌ ERRO no banco: {str(e)}")


def test_backend_health():
    """Teste: Health check do backend"""
    print("\n🧪 TESTE 0: Health check do backend")
    print("-" * 50)

    try:
        response = httpx.get(f"{TEST_BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend online: {data}")
            return True
        else:
            print(f"❌ Backend respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERRO: Não foi possível conectar ao backend")
        print(f"   Verifique se está rodando: uvicorn backend:app --reload")
        print(f"   URL: {TEST_BACKEND_URL}")
        return False


async def main():
    """Executar todos os testes"""
    print("=" * 50)
    print("🔧 TESTES DE INTEGRAÇÃO - MERCADO PAGO")
    print("=" * 50)

    # Teste de health
    if not test_backend_health():
        print("\n❌ Backend não está disponível. Abortando testes.")
        return

    # Testes de banco de dados
    test_database()

    # Testes de API
    preference_id = await test_payment_creation()
    status = await test_payment_status(TEST_USER_EMAIL)
    token = await test_unlock_report(TEST_USER_EMAIL)
    await test_verify_token(token)

    print("\n" + "=" * 50)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
