import customtkinter as ctk
from database import conectar
from utils import campo, converter_valor, dinheiro
from tkinter import messagebox, simpledialog



class TelaContratos:
    def montar_contratos(self):
        formulario = ctk.CTkFrame(self.aba_contratos)
        formulario.pack(fill="x", padx=10, pady=10)

        self.contrato_cliente = ctk.CTkOptionMenu(formulario, values=["Carregando..."])
        self.contrato_cliente.pack(side="left", padx=5, pady=10)

        self.contrato_obra = campo(formulario, "Nome da obra", 200)
        self.contrato_obra.pack(side="left", padx=5)

        self.contrato_servico = campo(formulario, "Serviço", 180)
        self.contrato_servico.pack(side="left", padx=5)

        self.contrato_valor = campo(formulario, "Valor do contrato", 150)
        self.contrato_valor.pack(side="left", padx=5)

        ctk.CTkButton(
            formulario,
            text="Cadastrar contrato",
            command=self.salvar_contrato
        ).pack(side="left", padx=5)

        self.tabela_contratos = self.montar_tabela(
            self.aba_contratos,
            ("ID", "Cliente", "Obra", "Serviço", "Valor")
        )

        botoes = ctk.CTkFrame(self.aba_contratos)
        botoes.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            botoes, text="Excluir selecionado",
            command=self.excluir_contrato
        ).pack(side="left", padx=5)
        self.tabela_contratos.bind("<Double-1>", self.editar_contrato)


    def atualizar_contratos(self):
        self.limpar_tabela(self.tabela_contratos)

        with conectar() as db:
            contratos = db.execute("""
                SELECT ct.id, cl.nome, ct.obra, ct.servico,
                       ct.valor + COALESCE(
                           (SELECT SUM(a.valor)
                            FROM aditivos a
                            WHERE a.contrato_id = ct.id), 0
                       ) AS valor_total
                FROM contratos ct
                JOIN clientes cl ON cl.id = ct.cliente_id
                ORDER BY ct.id DESC
            """).fetchall()

        self.ids_contratos = {}
        opcoes = []

        for contrato_id, cliente, obra, servico, valor in contratos:
            self.tabela_contratos.insert(
                "", "end",
                values=(contrato_id, cliente, obra, servico, dinheiro(valor))
            )

            texto = f"{contrato_id} - {cliente} - {obra}"
            self.ids_contratos[texto] = contrato_id
            opcoes.append(texto)

        if opcoes:
            self.recebimento_contrato.configure(values=opcoes)
            self.recebimento_contrato.set(opcoes[0])

            self.aditivo_contrato.configure(values=opcoes)
            self.aditivo_contrato.set(opcoes[0])
        else:
            mensagem = "Cadastre um contrato primeiro"

            self.recebimento_contrato.configure(values=[mensagem])
            self.recebimento_contrato.set(mensagem)

            self.aditivo_contrato.configure(values=[mensagem])
            self.aditivo_contrato.set(mensagem)


    def salvar_contrato(self):
        cliente_texto = self.contrato_cliente.get()
        cliente_id = self.ids_clientes.get(cliente_texto)

        if not cliente_id:
            messagebox.showwarning(
                "Cliente necessário", "Cadastre e selecione um cliente."
            )
            return

        obra = self.contrato_obra.get().strip()
        servico = self.contrato_servico.get().strip()
        texto_valor = self.contrato_valor.get()

        if not obra:
            messagebox.showwarning(
                "Campo obrigatório", "Informe o nome da obra."
            )
            return

        try:
            valor = converter_valor(texto_valor)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Valor inválido",
                "Informe um valor maior que zero. Exemplo: 1250,50"
            )
            return

        with conectar() as db:
            db.execute(
                """
                INSERT INTO contratos (cliente_id, obra, servico, valor)
                VALUES (?, ?, ?, ?)
                """,
                (cliente_id, obra, servico, valor)
            )

        self.contrato_obra.delete(0, "end")
        self.contrato_servico.delete(0, "end")
        self.contrato_valor.delete(0, "end")
        self.atualizar_telas()
        messagebox.showinfo("Concluído", "Contrato cadastrado.")


    def excluir_contrato(self):
        item = self.item_selecionado(self.tabela_contratos, "contrato")
        if not item:
            return

        contrato_id = int(item[0])

        with conectar() as db:
            tem_recebimentos = db.execute(
                "SELECT 1 FROM recebimentos WHERE contrato_id = ? LIMIT 1",
                (contrato_id,)
            ).fetchone()

        if tem_recebimentos:
            messagebox.showwarning(
                "Não é possível excluir",
                "Este contrato tem recebimentos. Exclua-os primeiro."
            )
            return

        if not messagebox.askyesno(
            "Confirmar exclusão", f"Excluir a obra '{item[2]}'?"
        ):
            return

        with conectar() as db:
            db.execute("DELETE FROM aditivos WHERE contrato_id = ?", (contrato_id,))
            db.execute("DELETE FROM contratos WHERE id = ?", (contrato_id,))

        self.atualizar_telas()

    def editar_contrato(self, _evento=None):
        item = self.item_selecionado(self.tabela_contratos, "contrato")
        if not item:
            return

        contrato_id = int(item[0])

        with conectar() as db:
            dados = db.execute(
                "SELECT obra, servico, valor FROM contratos WHERE id = ?",
                (contrato_id,)
            ).fetchone()

        if not dados:
            return

        obra = simpledialog.askstring(
            "Editar contrato", "Obra:", initialvalue=dados[0], parent=self
        )
        if obra is None:
            return

        servico = simpledialog.askstring(
            "Editar contrato", "Serviço:", initialvalue=dados[1], parent=self
        )
        if servico is None:
            return

        valor_texto = simpledialog.askstring(
            "Editar contrato",
            "Valor original do contrato:",
            initialvalue=str(dados[2]).replace(".", ","),
            parent=self
        )
        if valor_texto is None:
            return

        try:
            valor = converter_valor(valor_texto)
            if not obra.strip() or valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Dados inválidos", "Informe uma obra e um valor maior que zero."
            )
            return

        with conectar() as db:
            db.execute(
                "UPDATE contratos SET obra = ?, servico = ?, valor = ? WHERE id = ?",
                (obra.strip(), servico.strip(), valor, contrato_id)
            )

        self.atualizar_telas()
