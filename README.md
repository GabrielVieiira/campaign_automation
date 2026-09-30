# Campaign Management Platform (Plataforma de Gerenciamento de Campanhas)

Uma API backend para gerenciamento de campanhas de marketing digital, configurações de rastreamento e integrações externas (como o RedTrack).

## Stack Tecnológica
- **Python 3.13+**
- **FastAPI**
- **SQLAlchemy 2.0 + Alembic**
- **Pydantic**
- **SQLite (Desenvolvimento) / PostgreSQL (Produção)**
- **PyJWT (Autenticação)**
- **HTTPX (Cliente de API Externa)**

## Instruções de Configuração

### 1. Requisitos
- Python 3.13+
- Poetry (`pip install poetry`)

### 2. Instalação
```bash
poetry install
```

### 3. Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` (ou use o gerado por padrão):
```bash
cp .env.example .env
```
Certifique-se de configurar uma `JWT_SECRET_KEY` e uma `REDTRACK_API_KEY`.

### 4. Configuração do Banco de Dados
O `.env` padrão utiliza o SQLite (`sqlite:///./campaign_management.db`).
Execute as migrations para criar as tabelas no banco de dados:
```bash
poetry run alembic upgrade head
```

### 5. Executando a Aplicação
```bash
poetry run fastapi dev app/main.py
```
A documentação da API estará disponível em: http://localhost:8000/docs

## Executando os Testes
Os testes utilizam um banco de dados SQLite isolado e em memória.
```bash
poetry run pytest
```

## Linting & Verificação de Tipagem
```bash
poetry run ruff check app tests
poetry run ruff format app tests
poetry run mypy app tests
```

## Documentação
Consulte a pasta `docs/` para ver as decisões arquiteturais, visão geral das camadas e detalhes de integrações.
