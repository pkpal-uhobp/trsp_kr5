def task_payload(**overrides):
    payload = {
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты для основных сценариев",
        "status": "todo",
        "priority": 4,
    }
    payload.update(overrides)
    return payload


def test_create_task_success(client, user10_headers):
    response = client.post("/tasks", json=task_payload(), headers=user10_headers)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Подготовить тесты",
        "description": "Написать интеграционные тесты для основных сценариев",
        "status": "todo",
        "priority": 4,
        "owner_id": 10,
    }


def test_create_task_title_too_short_returns_422(client, user10_headers):
    response = client.post("/tasks", json=task_payload(title="ab"), headers=user10_headers)

    assert response.status_code == 422


def test_missing_user_header_returns_401(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_invalid_user_header_returns_401(client):
    response = client.get("/tasks", headers={"X-User-Id": "not-int"})

    assert response.status_code == 401


def test_user_sees_only_own_tasks(client, user10_headers, user20_headers):
    client.post("/tasks", json=task_payload(title="Задача пользователя 10"), headers=user10_headers)
    client.post("/tasks", json=task_payload(title="Задача пользователя 20"), headers=user20_headers)

    response = client.get("/tasks", headers=user10_headers)

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Задача пользователя 10"
    assert tasks[0]["owner_id"] == 10


def test_filter_tasks_by_status_and_min_priority(client, user10_headers):
    client.post("/tasks", json=task_payload(title="Низкий todo", status="todo", priority=2), headers=user10_headers)
    client.post("/tasks", json=task_payload(title="Высокий todo", status="todo", priority=5), headers=user10_headers)
    client.post("/tasks", json=task_payload(title="Высокий done", status="done", priority=5), headers=user10_headers)

    response = client.get("/tasks?status=todo&min_priority=4", headers=user10_headers)

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Высокий todo"]


def test_update_task_status_success(client, user10_headers):
    created = client.post("/tasks", json=task_payload(status="todo"), headers=user10_headers).json()

    response = client.patch(
        f"/tasks/{created['id']}/status",
        json={"status": "done"},
        headers=user10_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_foreign_or_missing_task_returns_404(client, user10_headers, user20_headers):
    created = client.post("/tasks", json=task_payload(), headers=user10_headers).json()

    foreign_response = client.get(f"/tasks/{created['id']}", headers=user20_headers)
    missing_response = client.get("/tasks/999", headers=user10_headers)

    assert foreign_response.status_code == 404
    assert missing_response.status_code == 404


def test_delete_task_success(client, user10_headers):
    created = client.post("/tasks", json=task_payload(), headers=user10_headers).json()

    delete_response = client.delete(f"/tasks/{created['id']}", headers=user10_headers)
    get_response = client.get(f"/tasks/{created['id']}", headers=user10_headers)

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 404
