# Documentação Técnica — SGC (Sistema de Gestão Comercial)

Disciplina: Desenvolvimento Web · Entrega 3 — Sistema Completo

---

## 1. Descrição do sistema

O SGC apoia o ciclo comercial de uma loja de informática: cadastro de clientes e
produtos, registro de vendas com baixa automática de estoque, autenticação por perfil
(ADMIN / FUNCIONARIO) e relatórios de vendas com gráfico anual. O sistema expõe uma
**API REST** (consumível por qualquer cliente) e uma **interface web** própria que a
utiliza.

## 2. Arquitetura

O projeto segue o padrão **MVT** do Django acrescido de uma camada de **API REST**
(Django REST Framework):

```
        Navegador (Interface Web)
   Templates Bootstrap + JavaScript (fetch)
                 │
   ┌─────────────┴──────────────┐
   │ Sessão Django (login web)  │   Autorização das telas
   │ JWT (consumo da API)       │   Authorization: Bearer <token>
   └─────────────┬──────────────┘
                 │  HTTP / JSON
          API REST (DRF ViewSets)
        Serializers (validação de dados)
                 │
        Camada de negócio
   (regras nos models + exceções personalizadas
            + handler global de exceções)
                 │
            Models (ORM Django)
                 │
              PostgreSQL
```

Camadas:

- **Apresentação:** templates HTML + Bootstrap 5 + Chart.js. As listagens de clientes
  e produtos consomem a API via `fetch` com token JWT.
- **API REST:** `ViewSets`/`APIView` do DRF, com `Serializers` validando entrada e saída.
- **Negócio:** regras encapsuladas nos models (ex.: `estoque_suficiente`,
  `possui_vendas`) e nos serializers; exceções de domínio próprias.
- **Persistência:** ORM do Django sobre PostgreSQL.

## 3. Padrões de projeto utilizados

- **MVT (Model–View–Template)** — organização base do Django.
- **Serializer / DTO** — `Serializers` do DRF separam o modelo de domínio da
  representação trafegada na API.
- **Repository (via ORM)** — o acesso a dados é mediado pelo `QuerySet`/`Manager`,
  isolando SQL da regra de negócio.
- **Token-based Authentication (JWT)** — autenticação stateless da API.
- **Exception Handler centralizado** — `sgc.exceptions.handler_global` padroniza o
  formato de erro (`{"erro": ...}`) e o status HTTP de todas as respostas da API.
- **Custom Exceptions** — `EstoqueInsuficienteException`, `ClienteComVendasException`,
  `VendaSemItensException`, `CPFDuplicadoException`, derivadas de `SGCException`.

## 4. Justificativa das decisões técnicas

**4.1. Dupla autenticação: sessão para a web, JWT para a API.**
A interface web usa **sessão Django** porque é o mecanismo nativo e seguro para
navegação por cookies (incluindo proteção CSRF nos formulários). A **API REST** usa
**JWT** por ser stateless e adequada a clientes externos. Para que a interface possa
consumir a API sem um segundo login, o endpoint `GET /auth/token-sessao/` emite um
*access token* JWT para o usuário já autenticado por sessão; o JavaScript das telas
usa esse token no cabeçalho `Authorization: Bearer`. Assim os dois mundos convivem sem
duplicar credenciais.

**4.2. Regras de negócio no domínio, não na view.**
Validações como CPF único, preço não-negativo, estoque suficiente e "cliente com vendas
não pode ser removido" ficam nos models/serializers, garantindo que sejam aplicadas
tanto pela API quanto pela interface web.

**4.3. Venda como operação atômica.**
O registro de venda roda dentro de `transaction.atomic` com `select_for_update` nos
produtos, evitando condições de corrida na baixa de estoque. Vendas não podem ser
editadas nem removidas (integridade do histórico).

**4.4. Erros padronizados.**
Um único *handler* global converte exceções de domínio e do DRF para um formato JSON
consistente, simplificando o tratamento no front-end.

## 5. Diagramas

- **Diagrama de Domínio:** `docs/` (ver PDF da modelagem).
- **Diagrama de Classes:** `docs/Diagrama-Classes.pdf`.
- **Diagrama Lógico do Banco:** `docs/Diagrama-Lógico.pdf`.
- **Script SQL de criação:** `docs/SGC-script-banco-v2.sql`.

Entidades principais: `Usuario`, `Cliente`, `Produto`, `Venda`, `ItemVenda`
(tabelas: `usuarios`, `clientes`, `produtos`, `vendas`, `itens_venda`).

## 6. Endpoints da API

Todas as rotas (exceto `/auth/login`) exigem `Authorization: Bearer <token>`.

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/auth/login` | Login; retorna access + refresh |
| POST | `/auth/refresh` | Renova o access token |
| GET  | `/auth/token-sessao/` | Token JWT para usuário com sessão web ativa |
| GET/POST | `/clientes/` | Listar / criar |
| GET/PUT/DELETE | `/clientes/{id}/` | Detalhar / editar / remover |
| GET/POST | `/produtos/` | Listar / criar |
| GET/PUT/DELETE | `/produtos/{id}/` | Detalhar / editar / remover |
| GET/POST | `/vendas/` | Listar / registrar |
| GET | `/vendas/{id}/` | Detalhar venda |
| GET | `/vendas/relatorio/periodo/` | Relatório por período |
| GET | `/vendas/relatorio/mensal/` | Dados mensais para o gráfico |

## 7. Como executar

```bash
git clone <url-do-repositorio>
cd sgc
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # editar credenciais do banco e SECRET_KEY
# criar o banco no PostgreSQL: CREATE DATABASE sgc;
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Interface web: `http://localhost:8000/web/login/` · Admin: `/admin/`

## 8. Testes

```bash
python manage.py test
```

Cobrem: CPF duplicado e inválido, preço negativo, estoque insuficiente, venda sem itens,
baixa de estoque após venda e proteção de rotas sem autenticação (19 testes).

## 9. Identidade visual

Nome **SGC** e paleta própria com azul institucional `#1F4E79` aplicada à sidebar,
marca e botões primários.

## 10. Repositório

GitHub: https://github.com/GuilhermeGouveia12/-SGC-Projeto-de-Desenvolviemento-Web

## 11. Autores

- Guilherme Gouveia Dalla Mutta
- Arthur Grangeiro Botelho
