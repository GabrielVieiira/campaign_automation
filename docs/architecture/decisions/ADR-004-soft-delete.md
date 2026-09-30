# ADR-004: Soft Delete (Exclusão Lógica)

## Status
Aceito

## Contexto
Dados relacionados a campanhas, configurações e contas de usuário raramente devem ser excluídos permanentemente, a fim de preservar trilhas de auditoria, relatórios históricos e prevenir a perda acidental de dados.

## Decisão
Todos os modelos críticos herdarão de `SoftDeleteMixin`, que fornece um carimbo de data/hora `deleted_at`.
Em vez de usar `DELETE FROM`, usaremos `UPDATE ... SET deleted_at = NOW()`.
Todas as funções `get_*` nos Seletores excluirão registros marcados como soft-delete por padrão (`deleted_at.is_(None)`), a menos que explicitamente solicitado por meio de uma flag `include_deleted=True`.

## Consequências
- **Positivas**: Fácil recuperação de dados, referências históricas mantidas intactas.
- **Negativas**: As consultas devem sempre lembrar de filtrar por `deleted_at IS NULL` (encapsulado nos seletores). Restrições de unicidade (unique constraints) frequentemente devem incluir o `deleted_at` para permitir a criação de um novo registro com o mesmo campo único de um registro excluído (ex: `email`).
