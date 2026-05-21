def test_health_route(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "env": "test"}
