"""Testes de integração para o endpoint de integridade (health)."""

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
