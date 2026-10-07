def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_http_error(client):
    resp = client.get("/bogus")
    assert resp.status_code == 404
    assert resp.json() == {"error": {"code": "NOT_FOUND", "message": "Not Found"}}
