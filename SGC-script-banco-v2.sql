-- =============================================================
-- SGC — Sistema de Gestão Comercial
-- Script de Criação do Banco de Dados
-- Banco: PostgreSQL
-- Entrega 1 — Modelagem e Arquitetura
-- =============================================================
--
-- IMPORTANTE: Este script é fornecido para fins de documentação
-- e avaliação acadêmica. Para executar o sistema, utilize o
-- comando do Django:
--
--   python manage.py migrate
--
-- O migrate cria todas as tabelas automaticamente e é o método
-- recomendado. Rodar este script manualmente em um banco que já
-- passou pelo migrate causará conflitos de tabelas duplicadas.
--
-- Para rodar este script em um banco limpo (sem migrate):
--   1. Crie o banco: CREATE DATABASE sgc;
--   2. Conecte no banco sgc
--   3. Execute este script a partir da seção 1 em diante
--      (ignorando o CREATE DATABASE abaixo)
-- =============================================================

-- -------------------------------------------------------------
-- 0. Criação do banco (executar conectado ao banco "postgres")
--    Ignorar se o banco sgc já existir.
-- -------------------------------------------------------------

-- CREATE DATABASE sgc
--     WITH
--     ENCODING = 'UTF8'
--     TEMPLATE = template0;

-- -------------------------------------------------------------
-- 1. Tipos customizados
-- -------------------------------------------------------------

CREATE TYPE perfil_usuario AS ENUM ('ADMIN', 'FUNCIONARIO');

-- -------------------------------------------------------------
-- 2. Tabela: usuarios
-- -------------------------------------------------------------

CREATE TABLE usuarios (
    id            SERIAL          PRIMARY KEY,
    username      VARCHAR(50)     NOT NULL UNIQUE,
    senha         VARCHAR(255)    NOT NULL,
    perfil        perfil_usuario  NOT NULL DEFAULT 'FUNCIONARIO',
    ativo         BOOLEAN         NOT NULL DEFAULT TRUE,
    is_superuser  BOOLEAN         NOT NULL DEFAULT FALSE,
    is_staff      BOOLEAN         NOT NULL DEFAULT FALSE,
    last_login    TIMESTAMP,
    criado_em     TIMESTAMP       NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  usuarios           IS 'Usuarios do sistema com controle de acesso por perfil.';
COMMENT ON COLUMN usuarios.senha     IS 'Senha armazenada como hash BCrypt/PBKDF2.';
COMMENT ON COLUMN usuarios.perfil    IS 'ADMIN: acesso total. FUNCIONARIO: acesso restrito.';

-- -------------------------------------------------------------
-- 3. Tabela: clientes
-- -------------------------------------------------------------

CREATE TABLE clientes (
    id            SERIAL       PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    cpf           CHAR(11)     NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL,
    telefone      VARCHAR(20),
    endereco      TEXT,
    criado_em     TIMESTAMP    NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP    NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_clientes_email
        CHECK (email ~* '^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'),

    CONSTRAINT chk_clientes_cpf_formato
        CHECK (LENGTH(cpf) = 11 AND cpf ~ '^[0-9]+$')
);

COMMENT ON TABLE  clientes     IS 'Clientes cadastrados na loja.';
COMMENT ON COLUMN clientes.cpf IS 'CPF sem formatacao (apenas digitos). Unico por cliente.';

-- -------------------------------------------------------------
-- 4. Tabela: produtos
-- -------------------------------------------------------------

CREATE TABLE produtos (
    id            SERIAL         PRIMARY KEY,
    nome          VARCHAR(100)   NOT NULL,
    descricao     TEXT,
    preco         DECIMAL(10, 2) NOT NULL,
    qtd_estoque   INTEGER        NOT NULL DEFAULT 0,
    estoque_min   INTEGER        NOT NULL DEFAULT 0,
    ativo         BOOLEAN        NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMP      NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP      NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_produtos_preco
        CHECK (preco >= 0),

    CONSTRAINT chk_produtos_qtd_estoque
        CHECK (qtd_estoque >= 0),

    CONSTRAINT chk_produtos_estoque_min
        CHECK (estoque_min >= 0)
);

COMMENT ON TABLE  produtos             IS 'Catalogo de produtos com controle de estoque.';
COMMENT ON COLUMN produtos.estoque_min IS 'Alerta quando qtd_estoque <= estoque_min.';

-- -------------------------------------------------------------
-- 5. Tabela: vendas
-- -------------------------------------------------------------

CREATE TABLE vendas (
    id          SERIAL         PRIMARY KEY,
    cliente_id  INTEGER        NOT NULL,
    usuario_id  INTEGER        NOT NULL,
    data        TIMESTAMP      NOT NULL DEFAULT NOW(),
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    criado_em   TIMESTAMP      NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_vendas_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes (id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_vendas_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_vendas_valor_total
        CHECK (valor_total >= 0)
);

COMMENT ON TABLE  vendas             IS 'Cabecalho das vendas realizadas.';
COMMENT ON COLUMN vendas.valor_total IS 'Calculado automaticamente via trigger a partir dos itens.';
COMMENT ON COLUMN vendas.cliente_id  IS 'FK clientes. ON DELETE RESTRICT impede remocao de cliente com vendas.';

-- -------------------------------------------------------------
-- 6. Tabela: itens_venda
-- -------------------------------------------------------------

CREATE TABLE itens_venda (
    id             SERIAL         PRIMARY KEY,
    venda_id       INTEGER        NOT NULL,
    produto_id     INTEGER        NOT NULL,
    quantidade     INTEGER        NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,

    CONSTRAINT fk_itens_venda
        FOREIGN KEY (venda_id)
        REFERENCES vendas (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_itens_produto
        FOREIGN KEY (produto_id)
        REFERENCES produtos (id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_itens_quantidade
        CHECK (quantidade > 0),

    CONSTRAINT chk_itens_preco_unitario
        CHECK (preco_unitario >= 0)
);

COMMENT ON TABLE  itens_venda                IS 'Itens individuais de cada venda.';
COMMENT ON COLUMN itens_venda.preco_unitario IS 'Snapshot do preco no momento da venda.';

-- -------------------------------------------------------------
-- 7. Indices
-- -------------------------------------------------------------

CREATE INDEX idx_clientes_cpf        ON clientes    (cpf);
CREATE INDEX idx_clientes_email      ON clientes    (email);
CREATE INDEX idx_vendas_cliente      ON vendas      (cliente_id);
CREATE INDEX idx_vendas_usuario      ON vendas      (usuario_id);
CREATE INDEX idx_vendas_data         ON vendas      (data);
CREATE INDEX idx_itens_venda_venda   ON itens_venda (venda_id);
CREATE INDEX idx_itens_venda_produto ON itens_venda (produto_id);

-- -------------------------------------------------------------
-- 8. Trigger: recalcular valor_total da venda automaticamente
-- -------------------------------------------------------------

CREATE OR REPLACE FUNCTION fn_atualizar_valor_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE vendas
    SET valor_total = (
        SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
        FROM itens_venda
        WHERE venda_id = COALESCE(NEW.venda_id, OLD.venda_id)
    )
    WHERE id = COALESCE(NEW.venda_id, OLD.venda_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_valor_total
AFTER INSERT OR UPDATE OR DELETE ON itens_venda
FOR EACH ROW EXECUTE FUNCTION fn_atualizar_valor_total();

-- =============================================================
-- Fim do script
-- =============================================================
