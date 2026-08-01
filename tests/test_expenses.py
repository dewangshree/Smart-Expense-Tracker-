import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Point storage at a temp file before importing the app
TEST_DATA_FILE = Path(__file__).parent / "test_expenses.json"


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """Redirect all storage I/O to a temporary file for each test."""
    import src.storage.json_storage as storage_module

    temp_file = tmp_path / "expenses.json"
    monkeypatch.setattr(storage_module, "DATA_FILE", temp_file)
    yield
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture
def client():
    from src.main import app

    return TestClient(app)


@pytest.fixture
def sample_payload():
    return {
        "title": "Coffee",
        "amount": 3.50,
        "category": "Food",
        "date": "2024-01-15",
    }


# ---------------------------------------------------------------------------
# Create expense
# ---------------------------------------------------------------------------


def test_create_expense_returns_201(client, sample_payload):
    response = client.post("/expenses", json=sample_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Coffee"
    assert data["amount"] == 3.50
    assert data["category"] == "Food"
    assert data["date"] == "2024-01-15"
    assert "id" in data


def test_create_expense_persists(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_multiple_expenses(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    client.post("/expenses", json={**sample_payload, "title": "Lunch", "amount": 12.0})
    response = client.get("/expenses")
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# Get expenses
# ---------------------------------------------------------------------------


def test_get_expenses_empty(client):
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_get_expenses_returns_all(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    client.post("/expenses", json={**sample_payload, "category": "Transport", "amount": 20.0})
    response = client.get("/expenses")
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# Category filter
# ---------------------------------------------------------------------------


def test_filter_by_category(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    client.post("/expenses", json={**sample_payload, "category": "Transport"})
    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["category"] == "Food"


def test_filter_by_category_case_insensitive(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    response = client.get("/expenses?category=food")
    assert len(response.json()) == 1


def test_filter_by_category_no_match(client, sample_payload):
    client.post("/expenses", json=sample_payload)
    response = client.get("/expenses?category=Healthcare")
    assert response.json() == []


# ---------------------------------------------------------------------------
# Total calculation
# ---------------------------------------------------------------------------


def test_total_all_expenses(client, sample_payload):
    client.post("/expenses", json=sample_payload)  # 3.50
    client.post("/expenses", json={**sample_payload, "amount": 6.50})  # 6.50
    response = client.get("/expenses/total")
    assert response.status_code == 200
    assert response.json()["total"] == 10.0


def test_total_by_category(client, sample_payload):
    client.post("/expenses", json=sample_payload)  # Food 3.50
    client.post("/expenses", json={**sample_payload, "category": "Transport", "amount": 50.0})
    response = client.get("/expenses/total?category=Food")
    assert response.json()["total"] == 3.50
    assert response.json()["category"] == "Food"


def test_total_empty_returns_zero(client):
    response = client.get("/expenses/total")
    assert response.json()["total"] == 0.0


# ---------------------------------------------------------------------------
# Delete expense
# ---------------------------------------------------------------------------


def test_delete_expense(client, sample_payload):
    created = client.post("/expenses", json=sample_payload).json()
    expense_id = created["id"]
    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204
    remaining = client.get("/expenses").json()
    assert all(e["id"] != expense_id for e in remaining)


def test_delete_nonexistent_expense_returns_404(client):
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/expenses/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Validation — invalid payloads
# ---------------------------------------------------------------------------


def test_create_expense_missing_title(client, sample_payload):
    payload = {k: v for k, v in sample_payload.items() if k != "title"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_empty_title(client, sample_payload):
    response = client.post("/expenses", json={**sample_payload, "title": "   "})
    assert response.status_code == 422


def test_create_expense_zero_amount(client, sample_payload):
    response = client.post("/expenses", json={**sample_payload, "amount": 0})
    assert response.status_code == 422


def test_create_expense_negative_amount(client, sample_payload):
    response = client.post("/expenses", json={**sample_payload, "amount": -5.0})
    assert response.status_code == 422


def test_create_expense_invalid_date(client, sample_payload):
    response = client.post("/expenses", json={**sample_payload, "date": "not-a-date"})
    assert response.status_code == 422


def test_create_expense_missing_category(client, sample_payload):
    payload = {k: v for k, v in sample_payload.items() if k != "category"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_empty_category(client, sample_payload):
    response = client.post("/expenses", json={**sample_payload, "category": ""})
    assert response.status_code == 422
