"""
Database Module - SQLite para armazenar status de pagamentos
"""

import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from threading import Lock

DATABASE_FILE = os.getenv("DATABASE_PATH", "payments.db")


class Database:
    def __init__(self, db_path=DATABASE_FILE):
        self.db_path = db_path
        self.lock = Lock()

    def get_connection(self):
        """Obter conexão com banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Inicializar tabelas do banco"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Tabela de pagamentos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT UNIQUE NOT NULL,
                    user_name TEXT,
                    preference_id TEXT,
                    mercado_pago_id TEXT,
                    status TEXT DEFAULT 'pending',
                    amount REAL,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Tabela de tokens de desbloqueio
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS unlock_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    used INTEGER DEFAULT 0
                )
                """
            )

            # Índices para performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_user_email ON payments(user_email)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_status ON payments(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_token ON unlock_tokens(token)"
            )

            conn.commit()
            conn.close()

    def save_payment(
        self, user_email: str, user_name: str, preference_id: str, status: str, amount: float
    ):
        """Salvar novo pagamento"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO payments 
                    (user_email, user_name, preference_id, status, amount, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (user_email, user_name, preference_id, status, amount),
                )
                conn.commit()
            finally:
                conn.close()

    def update_payment_status(
        self,
        user_email: str,
        status: str,
        mercado_pago_id: str = None,
        payment_method: str = None,
    ):
        """Atualizar status de pagamento"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE payments 
                    SET status = ?, mercado_pago_id = ?, payment_method = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_email = ?
                    """,
                    (status, mercado_pago_id, payment_method, user_email),
                )
                conn.commit()
            finally:
                conn.close()

    def get_payment_by_email(self, user_email: str):
        """Obter pagamento por email"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM payments WHERE user_email = ?", (user_email,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
        finally:
            conn.close()

    def get_payment_status(self, user_email: str):
        """Obter status de pagamento"""
        payment = self.get_payment_by_email(user_email)
        if payment:
            return payment["status"]
        return None

    def create_unlock_token(self, user_email: str):
        """Criar token de desbloqueio para usuário"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=30)

            try:
                cursor.execute(
                    """
                    INSERT INTO unlock_tokens (user_email, token, expires_at)
                    VALUES (?, ?, ?)
                    """,
                    (user_email, token, expires_at),
                )
                conn.commit()
                return token
            finally:
                conn.close()

    def verify_unlock_token(self, token: str):
        """Verificar se token de desbloqueio é válido"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM unlock_tokens 
                WHERE token = ? 
                AND expires_at > CURRENT_TIMESTAMP
                AND used = 0
                """,
                (token,),
            )
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def mark_token_used(self, token: str):
        """Marcar token como usado"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("UPDATE unlock_tokens SET used = 1 WHERE token = ?", (token,))
                conn.commit()
            finally:
                conn.close()

    def get_payment_stats(self):
        """Obter estatísticas de pagamentos"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT 
                    status, 
                    COUNT(*) as count, 
                    SUM(amount) as total
                FROM payments
                GROUP BY status
                """
            )
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
