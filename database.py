import sqlite3
import hashlib
import secrets
from utils import DB_PATH


# ---------- Banco de dados ----------
def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_hash(senha, salt=None):
    salt = salt or secrets.token_hex(16)
    resultado = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt.encode("utf-8"), 200_000
    )
    return salt, resultado.hex()


def verificar_senha(senha, salt, hash_salvo):
    _, hash_informado = criar_hash(senha, salt)
    return secrets.compare_digest(hash_informado, hash_salvo)


def inicializar_banco():
    with conectar() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT DEFAULT '',
                email TEXT DEFAULT '',
                usuario TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                senha_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT DEFAULT '',
                contato TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                obra TEXT NOT NULL,
                servico TEXT DEFAULT '',
                valor REAL NOT NULL,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            );

            CREATE TABLE IF NOT EXISTS recebimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                valor REAL NOT NULL,
                observacao TEXT DEFAULT '',
                FOREIGN KEY(contrato_id) REFERENCES contratos(id)
            );

            CREATE TABLE IF NOT EXISTS aditivos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY(contrato_id) REFERENCES contratos(id)
            );
        """)


def criar_usuario_inicial():
    with conectar() as db:
        existe = db.execute("SELECT id FROM usuarios LIMIT 1").fetchone()
        if existe:
            return

        # Troque a senha depois do primeiro acesso.
        usuario = "admin"
        senha ="admin"
        salt, senha_hash = criar_hash(senha)
        db.execute(
            "INSERT INTO usuarios (usuario, salt, senha_hash) VALUES (?, ?, ?)",
            (usuario, salt, senha_hash),
        )
        print(f"Usuário inicial: {usuario} | Senha inicial: {senha}")
