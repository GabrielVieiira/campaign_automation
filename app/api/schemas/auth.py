"""Esquemas de API para os endpoints de autenticação.

Os esquemas (schemas) definem o contrato entre a API e seus consumidores.
Eles NÃO devem conter lógica de negócios ou consultas ao banco de dados.

Estes modelos Pydantic são distintos dos modelos SQLAlchemy:
    - Os esquemas validam e serializam os dados de requisição/resposta HTTP.
    - Os modelos SQLAlchemy são mapeados para tabelas do banco de dados.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Corpo da requisição para POST /auth/login."""

    email: EmailStr = Field(..., description="Endereço de e-mail do usuário")
    password: str = Field(..., min_length=1, description="Senha do usuário")

    model_config = {
        "json_schema_extra": {
            "example": {"email": "usuario@exemplo.com", "password": "senha_secreta"}
        }
    }


class TokenResponse(BaseModel):
    """Corpo da resposta para uma autenticação bem-sucedida."""

    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token, sempre 'bearer'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }
