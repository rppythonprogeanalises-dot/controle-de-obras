import os
import sys
from pathlib import Path
from datetime import datetime
import customtkinter as ctk


# Define onde o banco de dados
if getattr(sys, "frozen", False):
    # Quando compilado salva na pasta de dados do usuário
    if sys.platform == "win32":
        PASTA_DADOS = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ControleDeObras"
    else:
        PASTA_DADOS = Path.home() / ".local" / "share" / "ControleDeObras"
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    DB_PATH = str(PASTA_DADOS / "controle_obras.db")
else:
    # Durante o desenvolvimento, mantém o banco na pasta do projeto
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(APP_DIR, "controle_obras.db")


# ---------- Utilidades ----------
def data_para_banco(texto):
    """Converte DD/MM/AAAA para AAAA-MM-DD."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").date().isoformat()


def data_para_tela(texto):
    texto = texto.strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            pass
    raise ValueError(f"Data inválida no banco: {texto!r}")


def dinheiro(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def converter_valor(texto):
    if isinstance(texto, (int, float)):
        return float(texto)
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def campo(parent, texto, largura=220):
    entrada = ctk.CTkEntry(parent, placeholder_text=texto, width=largura)
    return entrada
