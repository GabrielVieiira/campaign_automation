"""Testes de integração para as rotas de autenticação."""

from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import make_user


class TestLoginRoute:
    def test_login_success_returns_token(self, client: TestClient, db: Session):
        make_user(db, email="login@example.com", password="correct")

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "correct"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_failure_returns_401(self, client: TestClient, db: Session):
        make_user(db, email="real@example.com", password="correct")

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "real@example.com", "password": "wrong"},
        )

        assert response.status_code == 401
        assert "access_token" not in response.json()


class TestMeRoute:
    def test_get_me_returns_user_profile(self, client: TestClient, manager_user: User):
        # 1. Faz login para obter o token
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "manager@example.com", "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # 2. Obtém o perfil
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "manager@example.com"
        assert data["role"] == "manager"
        assert "hashed_password" not in data
        assert "deleted_at" not in data

    def test_get_me_without_token_returns_401(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client: TestClient):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido_xyz"},
        )
        assert response.status_code == 401
