# test_app.py
import pytest
from app import app, elo_delta
from unittest.mock import patch

# -----------------------------
# Test Elo
# -----------------------------
def test_elo_delta_basic():
    # Elo du gagnant > Elo du perdant
    delta = elo_delta(1200, 1000)
    assert isinstance(delta, int)
    assert delta > 0

    # Elo du gagnant < Elo du perdant
    delta2 = elo_delta(1000, 1200)
    assert delta2 > 0

# -----------------------------
# Test /health route
# -----------------------------
def test_health_route():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert "ok" in data
    assert "msgs" in data

# -----------------------------
# Test / route
# -----------------------------
@patch("app.cached_get_characters")
def test_index_route(mock_cached):
    from flask import url_for

    # Cas avec 2 personnages
    mock_cached.return_value = [{"_id": "1", "name": "A"}, {"_id": "2", "name": "B"}]
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Qui gagne" in response.data

    # Cas avec <2 personnages -> retourne 500
    mock_cached.return_value = [{"_id": "1", "name": "A"}]
    response2 = client.get("/")
    assert response2.status_code == 500
