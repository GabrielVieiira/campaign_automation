# ADR-005: SQLite para Dev, PostgreSQL para Produção

## Status
Aceito

## Contexto
Os desenvolvedores precisam de uma configuração sem atritos para o desenvolvimento local sem precisar rodar contêineres Docker ou configurar bancos de dados externos, enquanto a produção exige um RDBMS robusto, escalável e concorrente.

## Decisão
Usaremos **SQLite** para desenvolvimento e testes locais, e **PostgreSQL** para staging e produção.
Impomos isso através de variáveis de ambiente (`DATABASE_URL`).
O SQLAlchemy abstrai as diferenças, mas nós configuramos pragmas específicos do SQLite (como o modo `WAL`) na configuração da engine para melhorar a concorrência.
O Alembic é configurado com `render_as_batch=True` para suportar as capacidades limitadas de `ALTER TABLE` do SQLite durante as migrations.

## Consequências
- **Positivas**: Configuração local extremamente rápida. Ambiente de produção robusto.
- **Negativas**: Os desenvolvedores não podem usar facilmente recursos específicos do Postgres (como `JSONB`, `ARRAY` ou funções específicas) sem quebrar o ambiente de desenvolvimento SQLite. Devemos nos limitar aos tipos SQL padrão suportados por ambos.
