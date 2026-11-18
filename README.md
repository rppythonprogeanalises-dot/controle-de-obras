<img width="1107" height="732" alt="Captura de tela de 2026-11-17 22-37-40" src="https://github.com/user-attachments/assets/4abe4b54-bdfc-412c-852a-8ebac5170d5b" />
<img width="614" height="342" alt="Captura de tela de 2026-11-17 22-36-52" src="https://github.com/user-attachments/assets/270e60db-2646-4971-a2d7-bb0ea75186b1" />
# 🏗️ Controle de Obras e Serviços

Sistema desktop desenvolvido em Python para gestão financeira e operacional de obras, contratos, aditivos e recebimentos, com interface moderna e banco de dados local integrado.

---

## 📸 Visão Geral do Sistema

*(Dica: Depois de subir no GitHub, você pode editar este arquivo pelo próprio navegador e arrastar 2 ou 3 prints da tela de login e da tela principal aqui para ilustrar seu projeto!)*

---

## ✨ Funcionalidades Principais

* **Autenticação Segura:** Tela de login e cadastro de usuários com armazenamento de senhas criptografadas utilizando `salt` e hash (`hashlib`).
* **Gestão de Clientes:** Cadastro, edição e consulta de clientes.
* **Obras e Contratos:** Controle de obras vinculadas a cada cliente, com descrição de serviços e valores contratados.
* **Aditivos Contratuais:** Registro de acréscimos ou alterações de valores vinculados diretamente a cada contrato.
* **Controle de Recebimentos:** Lançamento de pagamentos recebidos com data e vínculo ao contrato correspondente.
* **Resumo Financeiro Dinâmico:**
  * Filtro por **Cliente específico** ou visão consolidada de **Todos os clientes**.
  * Filtro por **Período de datas** (`DD/MM/AAAA`).
  * Cálculo automático de **Total Contratado (+ Aditivos)**, **Total Recebido no Período**, **Total Recebido Geral** e **Saldo em Aberto**.
  * Tabela detalhada exibindo o saldo individual de cada obra.

---

## 🛠️ Tecnologias Utilizadas

* **[Python 3](https://python.org):** Linguagem principal do projeto.
* **[CustomTkinter](https://github.com):** Interface gráfica moderna e responsiva.
* **[SQLite3](https://sqlite.org):** Banco de dados relacional leve e embutido, sem necessidade de servidor externo.
* **[Pillow (PIL)](https://python-pillow.org):** Manipulação e exibição de imagens e logotipos na interface.

---

## 📁 Estrutura do Projeto

```text
ControleDeObras/
├── app.py              # Ponto de entrada, tela de login e janela principal
├── database.py         # Conexão, criação das tabelas e segurança de senhas
├── utils.py            # Formatação de datas, valores monetários e caminhos
├── telas/              # Módulos das abas do sistema
│   ├── aditivos.py
│   ├── clientes.py
│   ├── contratos.py
│   └── recebimentos.py
├── image/              # Ícones e logotipo da aplicação
├── requirements.txt    # Dependências do projeto
└── .gitignore          # Arquivos ignorados pelo controle de versão
```

---

## 🚀 Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rppythonprogeanalises-dot/controle-de-obras.git
cd controle-de-obras

   ```

2. **Crie e ative um ambiente virtual:**
   * **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   * **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie a aplicação:**
   ```bash
   python app.py
   ```

---

## 💻 Compatibilidade

O código foi estruturado de forma multiplataforma (`Linux` e `Windows`), gerenciando automaticamente caminhos de recursos e armazenamento seguro do banco de dados local.
