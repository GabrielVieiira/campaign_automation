"""API schemas for user-related endpoints."""

from pydantic import BaseModel, EmailStr

from app.shared.enums import Role


class UserResponse(BaseModel):
    """Public representation of a User.

    Excludes sensitive fields like hashed_password and deleted_at.
    """

    id: int
    email: EmailStr
    role: Role
    is_active: bool
    company_id: int | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "role": "manager",
                "is_active": True,
                "company_id": 1,
            }
        },
    }
