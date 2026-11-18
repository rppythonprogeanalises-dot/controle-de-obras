import sys
from datetime import date
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import ttk, messagebox

from database import conectar, inicializar_banco, verificar_senha, criar_hash
from utils import data_para_banco, dinheiro, campo
from telas.aditivos import TelaAditivos
from telas.recebimentos import TelaRecebimentos
from telas.contratos import TelaContratos
from telas.clientes import TelaClientes

# Localiza a pasta de imagens tanto no PyCharm quanto após compilado (PyInstaller / cx_Freeze)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    BASE_DIR = Path(__file__).resolve().parent

caminho_icone = BASE_DIR / "image" / "obra.png"


# ---------- Tela de login ----------
class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.acesso_liberado = False  # Controla se o sistema deve abrir depois
        self.geometry('600x300+350+100')
        self.resizable(False, False)
        self.title('Acessando: Controle de Obras')
        self.configure(fg_color='dark grey')


        # Carrega ícone e logotipo com segurança
        imagem = Image.open(caminho_icone)
        self.icone = ImageTk.PhotoImage(imagem)
        self.iconphoto(True, self.icone)

        self.frameLogo = ctk.CTkFrame(self, width=200, height=300, fg_color='dark grey', corner_radius=0)
        self.frameLogo.pack(side="left", fill="y")

        self.frameLogin = ctk.CTkFrame(self, width=400, height=300, fg_color='dark grey', corner_radius=0)
        self.frameLogin.pack(side="right", fill="both", expand=True)

        # Logotipo dentro da tela
        icone_logo = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(180, 180))
        logotipo = ctk.CTkFrame(self.frameLogo, border_width=4, border_color="#53868B")
        logotipo.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        logo_l = ctk.CTkLabel(logotipo, image=icone_logo, text="", fg_color="#53868B")
        logo_l.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Campos de Usuário e Senha
        ctk.CTkLabel(
            self.frameLogin, text='Usuário:', font=('Century Gothic', 18),
            fg_color='dark grey', text_color='black'
        ).place(x=15, y=75)
        self.user_entry = ttk.Entry(self.frameLogin, width=20)
        self.user_entry.place(x=120, y=80, width=240, height=24)

        ctk.CTkLabel(
            self.frameLogin, text='Senha:', font=('Century Gothic', 18),
            fg_color='dark grey', text_color='black'
        ).place(x=15, y=140)
        self.senh_entry = ttk.Entry(self.frameLogin, width=20, show='*')
        self.senh_entry.place(x=120, y=145, width=240, height=24)
        self.senh_entry.bind('<Return>', lambda _e: self.fazer_login())

        # Checkbox Mostrar Senha nas coordenadas exatas solicitadas
        self.check = ctk.BooleanVar(value=False)
        self.checkbutton = ctk.CTkCheckBox(
            self,
            text="Mostrar Senha",
            fg_color="#53868B",
            bg_color="dark grey",
            text_color="black",
            font=("Century Gothic", 11),
            variable=self.check,
            onvalue=True,
            offvalue=False,
            width=100,
            height=20,
            checkbox_width=16,
            checkbox_height=16,
            command=self.alterar_senha
        )
        self.checkbutton.place(x=465, y=175)

        # Botões principais
        self.botaoacesso = ctk.CTkButton(
            self.frameLogin, text='Acessar', width=120, font=('Century Gothic', 13, 'bold'),
            fg_color='#53868B', command=self.fazer_login)
        self.botaoacesso.place(x=150, y=205)

        self.bind('<Return>', lambda _event: self.fazer_login())
        self.bind('<KP_Enter>', lambda _event: self.fazer_login())

        self.botaocadastro = ctk.CTkButton(
            self.frameLogin, text='Cadastrar', width=120, font=('Century Gothic', 13),
            fg_color='#4A4A4A', command=self.abrir_cadastro
        )
        self.botaocadastro.place(x=150, y=245)

    def alterar_senha(self):
        if self.check.get():
            self.senh_entry.configure(show="")
        else:
            self.senh_entry.configure(show="*")

    def fechar_tela_login(self):
        # Cancela todos os agendamentos internos (update, check_dpi_scaling) antes de fechar
        for tarefa_id in self.tk.eval("after info").split():
            try:
                self.after_cancel(tarefa_id)
            except Exception:
                pass
        self.destroy()

    def fazer_login(self):
        usuario = self.user_entry.get().strip()
        senha = self.senh_entry.get()

        if not usuario or not senha:
            messagebox.showerror('Registro de Erro', 'Preencha corretamente nome de usuário e senha.')
            return

        with conectar() as db:
            registro = db.execute(
                "SELECT salt, senha_hash FROM usuarios WHERE usuario = ?",
                (usuario,),
            ).fetchone()

        if registro and verificar_senha(senha, registro[0], registro[1]):
            # messagebox.showinfo('Informações de Login', 'Acesso Confirmado: Bem-vindo!')
            self.acesso_liberado = True
            self.fechar_tela_login()
        else:
            messagebox.showerror(
                'Acesso Negado',
                'Usuário ou senha incorretos. Verifique os dados ou cadastre-se.'
            )


    def abrir_cadastro(self):
        # Esconde botões de login
        self.botaoacesso.place_forget()
        self.botaocadastro.place_forget()

        # Campos extras de cadastro
        self.nome_lbl = ctk.CTkLabel(
            self.frameLogin, text='Nome:', font=('Century Gothic', 18),
            fg_color='dark grey', text_color='black'
        )
        self.nome_lbl.place(x=15, y=10)
        self.nome_entry = ttk.Entry(self.frameLogin, width=20)
        self.nome_entry.place(x=120, y=15, width=240, height=24)

        self.email_lbl = ctk.CTkLabel(
            self.frameLogin, text='E-mail:', font=('Century Gothic', 18),
            fg_color='dark grey', text_color='black'
        )
        self.email_lbl.place(x=15, y=42)
        self.email_entry = ttk.Entry(self.frameLogin, width=20)
        self.email_entry.place(x=120, y=47, width=240, height=24)

        self.registrar_btn = ctk.CTkButton(
            self.frameLogin, text='Registrar', width=120, font=('Century Gothic', 13, 'bold'),
            fg_color='#53868B', command=self.salvar_cadastro
        )
        self.registrar_btn.place(x=150, y=205)

        self.voltar_btn = ctk.CTkButton(
            self.frameLogin, text='Voltar', width=120, font=('Century Gothic', 13),
            fg_color='#4A4A4A', command=self.voltar_login
        )
        self.voltar_btn.place(x=150, y=245)

    def salvar_cadastro(self):
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        usuario = self.user_entry.get().strip()
        senha = self.senh_entry.get()

        if not nome or not email or not usuario or not senha:
            messagebox.showerror('Registro de Erro', 'Não deixe nenhum campo vazio.')
            return

        salt, senha_hash = criar_hash(senha)

        try:
            with conectar() as db:
                db.execute(
                    "INSERT INTO usuarios (usuario, salt, senha_hash) VALUES (?, ?, ?)",
                    (usuario, salt, senha_hash)
                )
            messagebox.showinfo('Informações do Registro', 'Cadastro realizado com sucesso!')
            self.voltar_login()
        except Exception as erro:
            messagebox.showerror('Erro ao Cadastrar', f'Usuário já existe ou erro no banco:\n{erro}')

    def voltar_login(self):
        # Remove os campos de cadastro da tela
        self.nome_lbl.destroy()
        self.nome_entry.destroy()
        self.email_lbl.destroy()
        self.email_entry.destroy()
        self.registrar_btn.destroy()
        self.voltar_btn.destroy()

        # Limpa os campos e restaura botões originais
        self.user_entry.delete(0, "end")
        self.senh_entry.delete(0, "end")
        self.botaoacesso.place(x=150, y=205)
        self.botaocadastro.place(x=150, y=245)


# ---------- Aplicativo ----------
class Aplicativo(ctk.CTk, TelaAditivos, TelaRecebimentos, TelaContratos, TelaClientes):
    def __init__(self):
        super().__init__()
        self.title("Controle de Obras e Serviços")

        imagem_app = Image.open(caminho_icone)
        icone_app = ctk.CTkImage(light_image=imagem_app, dark_image=imagem_app, size=(60, 60))
        self.frameLogoApp = ctk.CTkFrame(
            self, width=68, height=68, fg_color="#53868B", border_width=2, border_color="#53868B"
        )
        self.frameLogoApp.place(x=15, y=8)
        logo_app = ctk.CTkLabel(self.frameLogoApp, image=icone_app, text="")
        logo_app.place(relx=0.5, rely=0.5, anchor="center")

        self.geometry("1100x700+150+100")
        self.minsize(900, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        titulo = ctk.CTkLabel(
            self, text="Controle de Obras e Serviços",
            font=("Arial", 25, "bold")
        )
        titulo.pack(pady=15)

        abas = ctk.CTkTabview(self)
        abas.pack(fill="both", expand=True, padx=15, pady=10)

        self.aba_resumo = abas.add("Resumo")
        self.aba_clientes = abas.add("Clientes")
        self.aba_contratos = abas.add("Obras e contratos")
        self.aba_recebimentos = abas.add("Recebimentos")
        self.aba_aditivos = abas.add("Aditivos")

        self.montar_resumo()
        self.montar_clientes()
        self.montar_contratos()
        self.montar_recebimentos()
        self.montar_aditivos()

        self.atualizar_telas()

    def montar_tabela(self, parent, colunas):
        tabela = ttk.Treeview(parent, columns=colunas, show="headings", height=12)
        for coluna in colunas:
            tabela.heading(coluna, text=coluna)
            tabela.column(coluna, width=140, anchor="w")
        tabela.pack(fill="both", expand=True, padx=10, pady=10)
        return tabela


    def montar_resumo(self):
        filtros = ctk.CTkFrame(self.aba_resumo)
        filtros.pack(fill="x", padx=10, pady=10)

        # Novo filtro de cliente
        ctk.CTkLabel(filtros, text="Cliente:").pack(side="left", padx=(10, 5))
        self.filtro_cliente_resumo = ctk.CTkOptionMenu(
            filtros,
            values=["Todos os clientes"],
            width=200,
            state="readonly",
            command=lambda _escolha: self.atualizar_resumo()  # Atualiza na hora ao trocar
        )
        self.filtro_cliente_resumo.set("Todos os clientes")
        self.filtro_cliente_resumo.pack(side="left", padx=5)

        ctk.CTkLabel(filtros, text="Período:").pack(side="left", padx=(15, 5))
        self.data_inicio = campo(filtros, "01/01/2026", 110)
        self.data_inicio.pack(side="left", padx=5)

        ctk.CTkLabel(filtros, text="Até:").pack(side="left", padx=5)
        self.data_fim = campo(filtros, date.today().strftime("%d/%m/%Y"), 110)
        self.data_fim.pack(side="left", padx=5)

        ctk.CTkButton(
            filtros, text="Atualizar resumo", command=self.atualizar_resumo
        ).pack(side="left", padx=10)

        # Quadro com os totais gerais
        self.texto_resumo = ctk.CTkLabel(
            self.aba_resumo, text="", font=("Arial", 16), justify="left"
        )
        self.texto_resumo.pack(anchor="w", padx=25, pady=(10, 5))

        ctk.CTkLabel(
            self.aba_resumo,
            text="Detalhamento por obra (o saldo considera o contrato + aditivos menos todos os recebimentos):",
            text_color="gray"
        ).pack(anchor="w", padx=25, pady=(5, 0))

        # Tabela detalhada por obra reaproveitando o seu montar_tabela()
        colunas_resumo = ("Cliente", "Obra", "Serviço", "Contratado", "Recebido", "Saldo")
        self.tabela_resumo = self.montar_tabela(self.aba_resumo, colunas_resumo)


    def limpar_tabela(self, tabela):
        for item in tabela.get_children():
            tabela.delete(item)

    def atualizar_telas(self):
        self.atualizar_clientes()
        self.atualizar_contratos()
        self.atualizar_recebimentos()
        self.carregar_clientes_resumo()
        self.atualizar_resumo()
        self.atualizar_aditivos()

    def carregar_clientes_resumo(self):
        with conectar() as db:
            clientes = db.execute("SELECT id, nome FROM clientes ORDER BY nome").fetchall()

        self.mapa_clientes_resumo = {nome: cid for cid, nome in clientes}
        opcoes = ["Todos os clientes"] + list(self.mapa_clientes_resumo.keys())
        self.filtro_cliente_resumo.configure(values=opcoes)

    def atualizar_resumo(self):
        inicio = self.data_inicio.get().strip() or "01/01/2026"
        fim = self.data_fim.get().strip() or date.today().strftime("%d/%m/%Y")

        try:
            inicio_banco = data_para_banco(inicio)
            fim_banco = data_para_banco(fim)

            if date.fromisoformat(inicio_banco) > date.fromisoformat(fim_banco):
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Data inválida",
                "Confira as datas. Use DD/MM/AAAA e verifique o período."
            )
            return

        cliente_selecionado = self.filtro_cliente_resumo.get()
        cliente_id = getattr(self, "mapa_clientes_resumo", {}).get(cliente_selecionado)

        with conectar() as db:
            if cliente_id is None:
                # 1. Totais gerais
                total_contratado = db.execute("""
                    SELECT COALESCE(SUM(
                        ct.valor + COALESCE(
                            (SELECT SUM(a.valor) FROM aditivos a WHERE a.contrato_id = ct.id), 0
                        )
                    ), 0)
                    FROM contratos ct
                """).fetchone()[0]

                total_recebido = db.execute(
                    "SELECT COALESCE(SUM(valor), 0) FROM recebimentos"
                ).fetchone()[0]

                recebido_periodo = db.execute(
                    "SELECT COALESCE(SUM(valor), 0) FROM recebimentos WHERE data BETWEEN ? AND ?",
                    (inicio_banco, fim_banco)
                ).fetchone()[0]

                # 2. Lista de todas as obras de todos os clientes
                obras = db.execute("""
                    SELECT
                        c.nome,
                        ct.obra,
                        ct.servico,
                        ct.valor + COALESCE((SELECT SUM(a.valor) FROM aditivos a WHERE a.contrato_id = ct.id), 0) AS contratado,
                        COALESCE((SELECT SUM(r.valor) FROM recebimentos r WHERE r.contrato_id = ct.id), 0) AS recebido
                    FROM contratos ct
                    JOIN clientes c ON c.id = ct.cliente_id
                    ORDER BY c.nome, ct.obra
                """).fetchall()
            else:
                # 1. Totais apenas do cliente selecionado
                total_contratado = db.execute("""
                    SELECT COALESCE(SUM(
                        ct.valor + COALESCE(
                            (SELECT SUM(a.valor) FROM aditivos a WHERE a.contrato_id = ct.id), 0
                        )
                    ), 0)
                    FROM contratos ct
                    WHERE ct.cliente_id = ?
                """, (cliente_id,)).fetchone()[0]

                total_recebido = db.execute("""
                    SELECT COALESCE(SUM(r.valor), 0)
                    FROM recebimentos r
                    JOIN contratos ct ON ct.id = r.contrato_id
                    WHERE ct.cliente_id = ?
                """, (cliente_id,)).fetchone()[0]

                recebido_periodo = db.execute("""
                    SELECT COALESCE(SUM(r.valor), 0)
                    FROM recebimentos r
                    JOIN contratos ct ON ct.id = r.contrato_id
                    WHERE ct.cliente_id = ? AND r.data BETWEEN ? AND ?
                """, (cliente_id, inicio_banco, fim_banco)).fetchone()[0]

                # 2. Lista das obras apenas daquele cliente
                obras = db.execute("""
                    SELECT
                        c.nome,
                        ct.obra,
                        ct.servico,
                        ct.valor + COALESCE((SELECT SUM(a.valor) FROM aditivos a WHERE a.contrato_id = ct.id), 0) AS contratado,
                        COALESCE((SELECT SUM(r.valor) FROM recebimentos r WHERE r.contrato_id = ct.id), 0) AS recebido
                    FROM contratos ct
                    JOIN clientes c ON c.id = ct.cliente_id
                    WHERE ct.cliente_id = ?
                    ORDER BY ct.obra
                """, (cliente_id,)).fetchall()

        saldo = total_contratado - total_recebido

        self.texto_resumo.configure(
            text=(
                f"Cliente: {cliente_selecionado}   |   "
                f"Total contratado: {dinheiro(total_contratado)}   |   "
                f"Recebido no período: {dinheiro(recebido_periodo)}\n"
                f"Total recebido geral: {dinheiro(total_recebido)}   |   "
                f"Saldo em aberto: {dinheiro(saldo)}"
            )
        )

        # Limpa e preenche a tabela por obra
        self.limpar_tabela(self.tabela_resumo)
        for nome_cli, obra, servico, val_contratado, val_recebido in obras:
            saldo_obra = val_contratado - val_recebido
            self.tabela_resumo.insert(
                "",
                "end",
                values=(
                    nome_cli,
                    obra,
                    servico,
                    dinheiro(val_contratado),
                    dinheiro(val_recebido),
                    dinheiro(saldo_obra)
                )
            )

    def item_selecionado(self, tabela, tipo):
        selecao = tabela.selection()
        if not selecao:
            messagebox.showwarning("Seleção necessária", f"Selecione um {tipo}.")
            return None
        return tabela.item(selecao[0], "values")


if __name__ == "__main__":
    inicializar_banco()

    janela_login = TelaLogin()
    janela_login.mainloop()

    if janela_login.acesso_liberado:
        app = Aplicativo()
        app.mainloop()
