# Camadas da Arquitetura

O backend é estritamente dividido nas seguintes camadas:

## 1. Camada de API (`app/api`)
- **Responsabilidade**: Lidar com requisições HTTP recebidas, processar payloads, validar dados de entrada, chamar o service apropriado e formatar a resposta HTTP.
- **Regras**:
  - SEM lógica de negócios.
  - SEM consultas ao banco de dados (não use `db.query` aqui).
  - As rotas devem receber dependências (como `db: Session`, `current_user: User`) por meio de injeção.
- **Componentes Principais**:
  - `routes/`: Roteadores do FastAPI.
  - `schemas/`: Modelos do Pydantic para validação de requisição/resposta.
  - `dependencies/`: Dependências reutilizáveis do FastAPI (autenticação, banco de dados).

## 2. Camada de Aplicação (`app/services`)
- **Responsabilidade**: Conter a lógica de negócios central (Casos de Uso) e orquestrar as chamadas entre o banco de dados, integrações externas e seletores.
- **Regras**:
  - SEM lógica específica de HTTP (nada de `Request`, `Response` ou `HTTPException`).
  - As funções devem levantar exceções de domínio (`app/shared/exceptions.py`) quando regras forem violadas.
  - Recebe o `db: Session` como um argumento para realizar gravações (writes).
- **Componentes Principais**:
  - `auth_service.py`, `campaign_service.py`, etc.

## 3. Camada de Dados (`app/models` & `app/selectors`)
- **Responsabilidade**: Definir o esquema do banco de dados e encapsular as consultas de leitura (reads).
- **Regras (Modelos)**:
  - Bases declarativas do SQLAlchemy.
  - Herdar de `SoftDeleteMixin` quando aplicável.
- **Regras (Seletores)**:
  - Todas as consultas complexas de leitura do banco de dados ficam aqui. Os services chamam os seletores para buscar dados.
  - Exemplo: usar `get_user_by_email(db, email)` em vez de `db.query(User).filter...` dentro de um service.

## 4. Camada de Integração (`app/integrations`)
- **Responsabilidade**: Comunicar-se com serviços externos (como o RedTrack).
- **Regras**:
  - Encapsular URLs de APIs externas, autenticação e tratamento de erros.
  - Traduzir erros HTTP externos (401, 404, 500) em exceções de domínio (ex: `RedTrackAuthError`).
  - Expor métodos Python limpos (ex: `get_campaigns()`) retornando estruturas de dados analisadas e formatadas.
