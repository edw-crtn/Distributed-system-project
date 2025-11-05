# tests/test_app.py
import pytest
from unittest.mock import patch
from app import app, elo_delta

# -------------------------------
# Test de la fonction elo_delta
# -------------------------------
def test_elo_delta_basic():
    delta = elo_delta(1000, 1000)
    # Pour des Elo identiques, delta doit être proche de 16 (k=32)
    assert delta in [15, 16, 17]

# -------------------------------
# Test des routes Flask
# -------------------------------
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_route(client):
    # On patch la fonction cached_get_characters pour qu'elle retourne toujours 2 persos fictifs
    with patch("app.cached_get_characters") as mock_chars:
        mock_chars.return_value = [
            {"_id": "1", "name": "Char1", "elo": 1000},
            {"_id": "2", "name": "Char2", "elo": 1000}
        ]
        response = client.get("/")
        assert response.status_code == 200
        assert b"Qui gagne" in response.data

def test_health_route(client):
    # On patch mongo_client et redis_client pour éviter des erreurs si pas de DB
    with patch("app.mongo_client") as mock_mongo, patch("app.redis_client") as mock_redis:
        mock_mongo.admin.command.return_value = {"ok": 1}
        mock_redis.ping.return_value = True

        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
