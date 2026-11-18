import customtkinter as ctk
from datetime import date
from database import conectar
from utils import campo, converter_valor, data_para_banco, dinheiro, data_para_tela
from tkinter import messagebox, simpledialog


class TelaAditivos:
    def __init__(self):
        self.ids_contratos = None
        self.aba_aditivos = None

    def salvar_aditivo(self):
        contrato_id = self.ids_contratos.get(self.aditivo_contrato.get())
        descricao = self.aditivo_descricao.get().strip()

        if not contrato_id:
            messagebox.showwarning("Contrato necessário", "Cadastre um contrato primeiro.")
            return
        if not descricao:
            messagebox.showwarning("Campo obrigatório", "Informe a descrição do aditivo.")
            return

        try:
            valor = converter_valor(self.aditivo_valor.get())
            data_banco = data_para_banco(self.aditivo_data.get())
            if valor < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Valor inválido",
                "Informe um valor válido. Exemplo: 500,00"
            )
            return

        with conectar() as db:
            db.execute(
                """INSERT INTO aditivos (contrato_id, descricao, valor, data)
                   VALUES (?, ?, ?, ?)""",
                (contrato_id, descricao, valor, data_banco)
            )

        self.aditivo_descricao.delete(0, "end")
        self.aditivo_valor.delete(0, "end")
        self.atualizar_telas()
        self.aditivo_data.delete(0, "end")
        self.aditivo_data.insert(0, date.today().strftime("%d/%m/%Y"))
        messagebox.showinfo("Concluído", "Aditivo registrado.")


    def montar_aditivos(self):
        formulario = ctk.CTkFrame(self.aba_aditivos)
        formulario.pack(fill="x", padx=10, pady=10)

        self.aditivo_contrato = ctk.CTkOptionMenu(
            formulario, values=["Cadastre um contrato primeiro"]
        )
        self.aditivo_contrato.pack(side="left", padx=5, pady=10)

        self.aditivo_descricao = campo(formulario, "Descrição do aditivo", 220)
        self.aditivo_descricao.pack(side="left", padx=5)

        self.aditivo_valor = campo(formulario, "Valor do aditivo", 150)
        self.aditivo_valor.pack(side="left", padx=5)

        self.aditivo_data = campo(formulario, date.today().strftime("%d/%m/%Y"), 130)
        self.aditivo_data.pack(side="left", padx=5)

        ctk.CTkButton(
            formulario, text="Adicionar aditivo",
            command=self.salvar_aditivo
        ).pack(side="left", padx=5)

        self.tabela_aditivos = self.montar_tabela(
            self.aba_aditivos,
            ("ID", "Cliente", "Obra", "Descrição", "Valor", "Data")
        )

        botoes = ctk.CTkFrame(self.aba_aditivos)
        botoes.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            botoes, text="Excluir selecionado",
            command=self.excluir_aditivo
        ).pack(side="left", padx=5)
        self.tabela_aditivos.bind("<Double-1>", self.editar_aditivo)


    def atualizar_aditivos(self):
        self.limpar_tabela(self.tabela_aditivos)

        with conectar() as db:
            registros = db.execute("""
                SELECT a.id, c.nome, ct.obra, a.descricao, a.valor, a.data
                FROM aditivos a
                JOIN contratos ct ON ct.id = a.contrato_id
                JOIN clientes c ON c.id = ct.cliente_id
                ORDER BY a.id DESC
            """).fetchall()

        for registro in registros:
            self.tabela_aditivos.insert(
                "", "end",
                values=(
                    registro[0], registro[1], registro[2],
                    registro[3],
                    dinheiro(converter_valor(registro[4])),
                    data_para_tela(registro[5])
                ))


    def excluir_aditivo(self):
        item = self.item_selecionado(self.tabela_aditivos, "aditivo")
        if not item:
            return

        aditivo_id = int(item[0])

        if not messagebox.askyesno(
                "Confirmar exclusão",
                f"Excluir o aditivo '{item[3]}'?"
        ):
            return

        with conectar() as db:
            db.execute("DELETE FROM aditivos WHERE id = ?", (aditivo_id,))

        self.atualizar_telas()


    def editar_aditivo(self, _evento=None):
        item = self.item_selecionado(self.tabela_aditivos, "aditivo")
        if not item:
            return

        aditivo_id = int(item[0])

        with conectar() as db:
            dados = db.execute(
                "SELECT descricao, valor, data FROM aditivos WHERE id = ?",
                (aditivo_id,)
            ).fetchone()

        if not dados:
            return

        descricao = simpledialog.askstring(
            "Editar aditivo", "Descrição:", initialvalue=data_para_tela(dados[0]), parent=self
        )
        if descricao is None:
            return

        valor_texto = simpledialog.askstring(
            "Editar aditivo",
            "Valor (use negativo para reduzir o contrato):",
            initialvalue=data_para_tela(dados[0]),
            parent=self
        )
        if valor_texto is None:
            return

        data_texto = simpledialog.askstring(
            "Editar aditivo",
            "Data (AAAA-MM-DD):",
            initialvalue=dados[2],
            parent=self
        )
        if data_texto is None:
            return

        try:
            valor = converter_valor(valor_texto)
            date.fromisoformat(data_texto.strip())
            if not descricao.strip() or valor == 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Dados inválidos",
                "Informe uma descrição, um valor diferente de zero e uma data válida."
            )
            return

        with conectar() as db:
            db.execute(
                """UPDATE aditivos
                   SET descricao = ?, valor = ?, data = ?
                   WHERE id = ?""",
                (descricao.strip(), valor, data_texto.strip(), aditivo_id)
            )

        self.atualizar_telas()
