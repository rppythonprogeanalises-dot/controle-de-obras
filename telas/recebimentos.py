import customtkinter as ctk
from utils import campo, converter_valor, data_para_banco, dinheiro, data_para_tela
from datetime import date
from tkinter import ttk, messagebox, simpledialog
from database import conectar


class TelaRecebimentos:
    def montar_recebimentos(self):
        formulario = ctk.CTkFrame(self.aba_recebimentos)
        formulario.pack(fill="x", padx=10, pady=10)

        self.recebimento_contrato = ctk.CTkOptionMenu(
            formulario,
            values=["Cadastre um contrato primeiro"]
        )
        self.recebimento_contrato.pack(side="left", padx=5, pady=10)

        self.recebimento_data = campo(formulario, date.today().strftime("%d/%m/%Y"), 130)
        self.recebimento_data.pack(side="left", padx=5)

        self.recebimento_valor = campo(
            formulario, "Valor recebido", 150
        )
        self.recebimento_valor.pack(side="left", padx=5)

        self.recebimento_observacao = campo(
            formulario, "Medição ou observação", 220
        )
        self.recebimento_observacao.pack(side="left", padx=5)

        ctk.CTkButton(
            formulario,
            text="Registrar recebimento",
            command=self.salvar_recebimento
        ).pack(side="left", padx=5)

        self.tabela_recebimentos = self.montar_tabela(
            self.aba_recebimentos,
            ("ID", "Data", "Cliente", "Obra", "Valor", "Observação")
        )

        botoes = ctk.CTkFrame(self.aba_recebimentos)
        botoes.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            botoes, text="Excluir selecionado",
            command=self.excluir_recebimento
        ).pack(side="left", padx=5)
        self.tabela_recebimentos.bind("<Double-1>", self.editar_recebimento)


    def atualizar_recebimentos(self):
        self.limpar_tabela(self.tabela_recebimentos)

        with conectar() as db:
            recebimentos = db.execute(
                """
                SELECT recebimentos.id, recebimentos.data, clientes.nome,
                       contratos.obra, recebimentos.valor,
                       recebimentos.observacao
                FROM recebimentos
                JOIN contratos
                    ON contratos.id = recebimentos.contrato_id
                JOIN clientes
                    ON clientes.id = contratos.cliente_id
                ORDER BY recebimentos.data DESC, recebimentos.id DESC
                """
            ).fetchall()

        for registro in recebimentos:
            recebimento_id, data_registro, cliente, obra, valor, observacao = registro

            self.tabela_recebimentos.insert(
                "",
                "end",
                values=(
                    recebimento_id,
                    data_para_tela(data_registro),
                    cliente,
                    obra,
                    dinheiro(valor),
                    observacao
                )
            )


    def salvar_recebimento(self):
        contrato_texto = self.recebimento_contrato.get()
        contrato_id = self.ids_contratos.get(contrato_texto)

        if not contrato_id:
            messagebox.showwarning(
                "Contrato necessário",
                "Cadastre e selecione um contrato."
            )
            return

        try:
            data_banco = data_para_banco(self.recebimento_data.get())
        except ValueError:
            messagebox.showwarning(
                "Data inválida",
                "Informe a data no formato DD/MM/AAAA. Exemplo: 25/03/2026."
            )
            return

        try:
            valor = converter_valor(self.recebimento_valor.get())
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Valor inválido",
                "Informe um valor maior que zero. Exemplo: 500,00"
            )
            return

        observacao = self.recebimento_observacao.get().strip()

        with conectar() as db:
            db.execute(
                """
                INSERT INTO recebimentos
                    (contrato_id, data, valor, observacao)
                VALUES (?, ?, ?, ?)
                """,
                (contrato_id, data_banco, valor, observacao)
            )

        self.recebimento_data.delete(0, "end")
        self.recebimento_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.recebimento_valor.delete(0, "end")
        self.recebimento_observacao.delete(0, "end")
        self.atualizar_telas()
        messagebox.showinfo("Concluído", "Recebimento registrado.")


    def excluir_recebimento(self):
        item = self.item_selecionado(
            self.tabela_recebimentos, "recebimento"
        )
        if not item:
            return

        recebimento_id = int(item[0])

        if not messagebox.askyesno(
                "Confirmar exclusão",
                f"Excluir o recebimento de {item[4]}?"
        ):
            return

        with conectar() as db:
            db.execute(
                "DELETE FROM recebimentos WHERE id = ?", (recebimento_id,)
            )

        self.atualizar_telas()

    def editar_recebimento(self, _evento=None):
        item = self.item_selecionado(
            self.tabela_recebimentos, "recebimento"
        )
        if not item:
            return

        recebimento_id = int(item[0])

        with conectar() as db:
            dados = db.execute(
                "SELECT data, valor, observacao FROM recebimentos WHERE id = ?",
                (recebimento_id,)
            ).fetchone()

        if not dados:
            return

        data_texto = simpledialog.askstring(
            "Editar recebimento",
            "Data (DD/MM/AAAA):",
            initialvalue=dados[0],
            parent=self
        )
        if data_texto is None:
            return

        valor_texto = simpledialog.askstring(
            "Editar recebimento",
            "Valor:",
            initialvalue=data_para_tela(dados[0]),
            parent=self
        )
        if valor_texto is None:
            return

        observacao = simpledialog.askstring(
            "Editar recebimento",
            "Observação:",
            initialvalue=data_para_tela(dados[0]),
            parent=self
        )
        if observacao is None:
            return

        try:
            data_banco = data_para_banco(data_texto)
            valor = converter_valor(valor_texto)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Dados inválidos",
                "Use uma data válida no formato DD/MM/AAAA e um valor maior que zero."
            )
            return

        with conectar() as db:
            db.execute(
                """UPDATE recebimentos
                   SET data = ?, valor = ?, observacao = ?
                   WHERE id = ?""",
                (data_banco, valor, observacao.strip(), recebimento_id)
            )

        self.atualizar_telas()
