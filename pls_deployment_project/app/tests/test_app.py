import os

os.environ.setdefault("DRY_RUN", "1")
os.environ.setdefault("ALLOWED_ORIGINS", '["*"]')

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_summarize_returns_text():
    client = TestClient(app)
    article = " ".join(["Medical" for _ in range(30)])
    response = client.post(
        "/api/v1/summarize",
        json={
            "article": article,
            "no_repeat_ngram_size": 4,
            "repetition_penalty": 1.5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data and len(data["summary"]) > 10
    assert "readability" in data
    assert "source" in data["readability"] and "generated" in data["readability"]


def test_classify_single_text():
    client = TestClient(app)
    text = " ".join(["Clinical", "trial", "data", "indicate", "efficacy"] * 5)
    response = client.post("/api/v1/classify", json={"text": text})
    assert response.status_code == 200
    payload = response.json()
    assert payload["label"] in {"pls", "non_pls"}
    assert 0.0 <= payload["score"] <= 1.0
