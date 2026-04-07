# SGC-Projeto-de-Desenvolviemento-Web

# Sistema de Gestão Comercial

## 1. Descrição

Sistema web desenvolvido para gestão de uma loja de informática, permitindo o controle de clientes, produtos, vendas e relatórios.

---

## 2. Funcionalidades

* Cadastro, edição e remoção de clientes
* Validação de CPF único
* Cadastro e controle de produtos
* Controle de estoque
* Registro de vendas com cálculo automático
* Atualização de estoque após venda
* Autenticação de usuários
* Geração de relatórios de vendas

---

## 3. Tecnologias Utilizadas

* Linguagem: Python
* Framework: Django
* Banco de Dados: PostgreSQL
* Versionamento: GitHub

---

## 4. Arquitetura

O sistema segue o padrão MVT (Model-View-Template), organizado em:

* Model: manipulação de dados
* View: regras de negócio
* Template: interface do usuário

---

## 5. Banco de Dados

Tabelas principais:

* usuarios
* clientes
* produtos
* vendas
* itens_venda

---
## 6. Padrões de Projeto Escolhidos

| Padrão                              | Aplicação no Projeto                                                                 |
|-------------------------------------|--------------------------------------------------------------------------------------|
| **MVT (Model-View-Template)**       | Separação entre dados, lógica e apresentação, padrão nativo do Django                |
| **Repository Pattern (via ORM)**    | Acesso ao banco de dados centralizado nos Models do Django                           |
| **Token-based Authentication (JWT)**| Autenticação stateless, sem necessidade de sessões armazenadas no servidor           |
| **REST (Representational State Transfer)** | Comunicação padronizada entre frontend e backend via HTTP/JSON                |

### Justificativa das Tecnologias

A escolha do **Django** em conjunto com o **Django REST Framework** se justifica pela maturidade do ecossistema, alta produtividade proporcionada pelo ORM e suporte nativo a funcionalidades essenciais como serialização de dados, autenticação e paginação de resultados.

O **PostgreSQL** foi selecionado como sistema de gerenciamento de banco de dados devido à sua robustez, suporte avançado a transações e conformidade com padrões relacionais, garantindo a integridade dos dados no contexto de vendas.
---

## 7. Autores

* Guilherme Gouveia Dalla Mutta
* Arthur Grangeiro Botelho Henrique Tomaz
