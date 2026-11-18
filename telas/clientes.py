import customtkinter as ctk
from tkinter import messagebox, simpledialog
from database import conectar
from utils import campo


class TelaClientes:
    def montar_clientes(self):
        formulario = ctk.CTkFrame(self.aba_clientes)
        formulario.pack(fill="x", padx=10, pady=10)

        self.cliente_nome = campo(formulario, "Nome do cliente - cadastrar", 260)
        self.cliente_nome.pack(side="left", padx=5, pady=10)

        self.cliente_documento = campo(formulario, "CPF/CNPJ", 180)
        self.cliente_documento.pack(side="left", padx=5)

        self.cliente_contato = campo(formulario, "Telefone ou e-mail", 220)
        self.cliente_contato.pack(side="left", padx=5)

        ctk.CTkButton(
            formulario, text="Cadastrar cliente", command=self.salvar_cliente
        ).pack(side="left", padx=5)

        self.tabela_clientes = self.montar_tabela(
            self.aba_clientes, ("ID", "Cliente", "Documento", "Contato")
        )

        botoes = ctk.CTkFrame(self.aba_clientes)
        botoes.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            botoes, text="Excluir selecionado",
            command=self.excluir_cliente
        ).pack(side="left", padx=5)
        self.tabela_clientes.bind("<Double-1>", self.editar_cliente)


    def atualizar_clientes(self):
        self.limpar_tabela(self.tabela_clientes)

        with conectar() as db:
            clientes = db.execute(
                """
                SELECT id, nome, documento, contato
                FROM clientes
                ORDER BY nome
                """
            ).fetchall()

        self.ids_clientes = {}

        opcoes = []
        for cliente_id, nome, documento, contato in clientes:
            self.tabela_clientes.insert(
                "",
                "end",
                values=(cliente_id, nome, documento, contato)
            )
            texto = f"{cliente_id} - {nome}"
            self.ids_clientes[texto] = cliente_id
            opcoes.append(texto)

        if opcoes:
            self.contrato_cliente.configure(values=opcoes)
            self.contrato_cliente.set(opcoes[0])
        else:
            self.contrato_cliente.configure(values=["Cadastre um cliente"])
            self.contrato_cliente.set("Cadastre um cliente")


    def salvar_cliente(self):
        nome = self.cliente_nome.get().strip()
        documento = self.cliente_documento.get().strip()
        contato = self.cliente_contato.get().strip()

        if not nome:
            messagebox.showwarning(
                "Campo obrigatório", "Informe o nome do cliente."
            )
            return

        with conectar() as db:
            db.execute(
                """
                INSERT INTO clientes (nome, documento, contato)
                VALUES (?, ?, ?)
                """,
                (nome, documento, contato)
            )

        self.cliente_nome.delete(0, "end")
        self.cliente_documento.delete(0, "end")
        self.cliente_contato.delete(0, "end")
        self.atualizar_telas()
        messagebox.showinfo("Concluído", "Cliente cadastrado.")


    def excluir_cliente(self):
        item = self.item_selecionado(self.tabela_clientes, "cliente")
        if not item:
            return
        cliente_id = int(item[0])

        with conectar() as db:
            tem_contratos = db.execute(
                "SELECT 1 FROM contratos WHERE cliente_id = ?", (cliente_id,)
            ).fetchone()

        if tem_contratos:
            messagebox.showwarning(
                "Não é possível excluir",
                "Este cliente possui contratos. Exclua primeiro os recebimentos, "
                "aditivos e contratos vinculados."
            )
            return

        if messagebox.askyesno("Confirmar", f"Excluir o cliente {item[1]}?"):
            with conectar() as db:
                db.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            self.atualizar_telas()

    def editar_cliente(self, _evento=None):
        item = self.item_selecionado(self.tabela_clientes, "cliente")
        if not item:
            return

        cliente_id = int(item[0])

        nome = simpledialog.askstring(
            "Editar cliente", "Nome:", initialvalue=item[1]
        )
        if nome is None:
            return

        nome = nome.strip()
        if not nome:
            messagebox.showwarning(
                "Campo obrigatório", "O nome do cliente não pode ficar vazio."
            )
            return

        documento = simpledialog.askstring(
            "Editar cliente", "CPF/CNPJ:", initialvalue=item[2]
        )
        if documento is None:
            return

        contato = simpledialog.askstring(
            "Editar cliente", "Telefone ou e-mail:", initialvalue=item[3]
        )
        if contato is None:
            return

        with conectar() as db:
            db.execute(
                """
                UPDATE clientes
                SET nome = ?, documento = ?, contato = ?
                WHERE id = ?
                """,
                (nome, documento.strip(), contato.strip(), cliente_id)
            )

        self.atualizar_telas()
        messagebox.showinfo("Concluído", "Cliente atualizado.")
