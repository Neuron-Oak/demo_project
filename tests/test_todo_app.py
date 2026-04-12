import tempfile
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.todo_app import create_app


@pytest.fixture()
def client():
    temp_dir = tempfile.TemporaryDirectory()
    db_path = Path(temp_dir.name) / "test.db"
    app = create_app({"TESTING": True, "DATABASE": str(db_path)})

    with app.test_client() as test_client:
        yield test_client

    temp_dir.cleanup()


def create_sample(client, title="Buy milk", description="2L", tags="home"):
    response = client.post(
        "/api/todos",
        json={"title": title, "description": description, "tags": tags},
    )
    assert response.status_code == 201
    return response.get_json()


def test_create_and_list_todo(client):
    created = create_sample(client)
    assert created["title"] == "Buy milk"
    assert created["done"] is False

    listed = client.get("/api/todos")
    assert listed.status_code == 200
    payload = listed.get_json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Buy milk"


def test_toggle_and_filter(client):
    created = create_sample(client, title="Ship release")
    todo_id = created["id"]

    toggled = client.patch(f"/api/todos/{todo_id}/toggle")
    assert toggled.status_code == 200
    assert toggled.get_json()["done"] is True

    open_items = client.get("/api/todos?status=open").get_json()
    done_items = client.get("/api/todos?status=done").get_json()
    assert len(open_items) == 0
    assert len(done_items) == 1


def test_update_todo(client):
    created = create_sample(client)
    todo_id = created["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={
            "title": "Buy coffee beans",
            "description": "1kg",
            "tags": "errands",
            "done": True,
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Buy coffee beans"
    assert payload["done"] is True


def test_delete_todo(client):
    created = create_sample(client, title="Archive docs")
    todo_id = created["id"]

    deleted = client.delete(f"/api/todos/{todo_id}")
    assert deleted.status_code == 204

    listed = client.get("/api/todos").get_json()
    assert listed == []


def test_reject_empty_title(client):
    response = client.post("/api/todos", json={"title": "  "})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required."
