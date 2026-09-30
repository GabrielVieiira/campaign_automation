# Domínio de Empresas (Companies Domain)

## Visão Geral

As Empresas (Companies) representam os inquilinos (tenants) na plataforma. Embora o MVP use uma única empresa,
a arquitetura está preparada para ser multi-tenant (múltiplos inquilinos) completa.

## Contexto Delimitado (Bounded Context)

- Criação e gerenciamento do ciclo de vida da Empresa
- Associação com Usuários e configurações do RedTrack
- Futuro: cobrança, gerenciamento de planos, configurações por empresa

## Estado Atual (MVP)

Existe um único registro de empresa. A chave de API do RedTrack é compartilhada (lida a partir do ambiente - env).
Nenhum isolamento de múltiplas empresas (multi-company) é imposto no nível da API ainda.

## Arquivos Principais

| Arquivo | Responsabilidade |
|------|---------------|
| `app/models/company.py` | Modelo SQLAlchemy para Empresa (Company) |
| `app/models/redtrack_config.py` | Configuração do RedTrack por Empresa |
| `app/selectors/company_selector.py` | Consultas no BD (Queries) para Empresa |

## Modelo de Dados

```
Company
   ├── id, name, slug
   ├── created_at, updated_at, deleted_at (soft delete)
   │
   ├── users[]              → User.company_id
   └── redtrack_configurations[]  → RedTrackConfiguration.company_id
```

## Trabalhos Futuros

- API de gerenciamento de empresas (somente ADMIN)
- Gerenciamento de chave de API do RedTrack por empresa (criptografada em repouso)
- Isolamento de acesso no nível da empresa (Row-Level Security)
- Múltiplas contas RedTrack por Empresa
