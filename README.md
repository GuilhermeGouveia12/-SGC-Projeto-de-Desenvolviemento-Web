# SGC — Sistema de Gestão Comercial

Sistema web para gestão de uma loja de informática, com controle de clientes, produtos, vendas e relatórios.

---

## Sumário

1. [Descrição](#1-descrição)
2. [Tecnologias](#2-tecnologias)
3. [Arquitetura](#3-arquitetura)
4. [Pré-requisitos](#4-pré-requisitos)
5. [Como executar](#5-como-executar)
6. [Endpoints da API](#6-endpoints-da-api)
7. [Testes](#7-testes)
8. [Autores](#8-autores)

---

## 1. Descrição

O SGC apoia o ciclo comercial completo de uma loja de informática: cadastro de clientes e produtos, registro de vendas com atualização automática de estoque, autenticação por perfil (ADMIN/FUNCIONARIO) via JWT e relatórios de vendas com gráfico anual.

---

## 2. Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Framework Web | Django 4.2 |
| API REST | Django REST Framework 3.15 |
| Autenticação | SimpleJWT |
| Banco de Dados | PostgreSQL |
| Frontend | HTML + Bootstrap 5 + Chart.js |
| Versionamento | Git / GitHub |

---

## 3. Arquitetura

O sistema segue o padrão **MVT** do Django com uma camada adicional de **API REST**:

```
Interface Web (Templates Bootstrap)
        ↕ HTTP / JSON
    API REST (Django REST Framework)
    Autenticação JWT (SimpleJWT)
        ↕
  Camada de Negócio (Views + Serializers)
  Exceções personalizadas + handler global
        ↕
    Models (ORM Django)
        ↕
      PostgreSQL
```

**Padrões utilizados:** MVT, Repository Pattern via ORM, Token-based Auth (JWT), REST.

---

## 4. Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e em execução
- Git

---

## 5. Como executar

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd sgc

# 2. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais do banco

# 5. Criar o banco no PostgreSQL
# psql -U postgres -c "CREATE DATABASE sgc;"

# 6. Aplicar migrações
python manage.py migrate

# 7. Criar superusuário
python manage.py createsuperuser

# 8. Iniciar o servidor
python manage.py runserver
```

Acesse a interface web em: `http://localhost:8000/web/`

---

## 6. Endpoints da API

Todas as rotas (exceto `/auth/login`) exigem `Authorization: Bearer <token>`.

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/auth/login` | Login; retorna access + refresh token |
| POST | `/auth/refresh` | Renova o access token |
| GET / POST | `/clientes/` | Listar / criar clientes |
| GET / PUT / DELETE | `/clientes/{id}/` | Detalhar / editar / remover cliente |
| GET / POST | `/produtos/` | Listar / criar produtos |
| GET / PUT / DELETE | `/produtos/{id}/` | Detalhar / editar / remover produto |
| GET | `/produtos/estoque-baixo/` | Produtos abaixo do estoque mínimo |
| GET / POST | `/vendas/` | Listar / registrar vendas |
| GET | `/vendas/{id}/` | Detalhar venda |
| GET | `/vendas/relatorio/periodo/` | Relatório por período (`?data_inicio=&data_fim=`) |
| GET | `/vendas/relatorio/mensal/` | Dados mensais para gráfico (`?ano=2025`) |

---

## 7. Testes

```bash
python manage.py test apps.clientes apps.produtos apps.vendas
```

Os testes cobrem: criação, validação de CPF duplicado, CPF inválido, preço negativo, estoque insuficiente, venda sem itens, atualização de estoque após venda e proteção de rotas sem autenticação.

---

## 8. Autores

- Guilherme Gouveia Dalla Mutta
- Arthur Grangeiro Botelho Henrique Tomaz

Disciplina: Desenvolvimento Web
