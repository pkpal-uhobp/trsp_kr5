def task_payload(**overrides):
    payload = {
        "title": "Маршрутизация",
        "description": "Проверка зависимостей и прав доступа",
        "status": "todo",
        "priority": 3,
    }
    payload.update(overrides)
    return payload


def test_users_me_returns_current_user(client, user10_headers):
    response = client.get("/users/me", headers=user10_headers)

    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_user_without_x_user_id_gets_401(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_regular_user_gets_403_for_admin_stats(client, user10_headers):
    response = client.get("/admin/stats", headers=user10_headers)

    assert response.status_code == 403


def test_admin_gets_stats_for_all_tasks(client, user10_headers, user20_headers, admin_headers):
    client.post("/tasks", json=task_payload(title="Todo 1", status="todo"), headers=user10_headers)
    client.post("/tasks", json=task_payload(title="Todo 2", status="todo"), headers=user20_headers)
    client.post("/tasks", json=task_payload(title="Progress", status="in_progress"), headers=user10_headers)
    client.post("/tasks", json=task_payload(title="Done 1", status="done"), headers=user20_headers)
    client.post("/tasks", json=task_payload(title="Done 2", status="done"), headers=user10_headers)

    response = client.get("/admin/stats", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 5,
        "by_status": {"todo": 2, "in_progress": 1, "done": 2},
    }


def test_regular_user_cannot_delete_foreign_task_via_tasks_route(client, user10_headers, user20_headers):
    created = client.post("/tasks", json=task_payload(), headers=user10_headers).json()

    response = client.delete(f"/tasks/{created['id']}", headers=user20_headers)

    assert response.status_code == 404


def test_admin_can_delete_foreign_task_via_admin_route(client, user10_headers, admin_headers):
    created = client.post("/tasks", json=task_payload(), headers=user10_headers).json()

    delete_response = client.delete(f"/admin/tasks/{created['id']}", headers=admin_headers)
    stats_response = client.get("/admin/stats", headers=admin_headers)

    assert delete_response.status_code == 204
    assert stats_response.json()["total_tasks"] == 0


def test_swagger_openapi_routes_are_grouped_by_tags(client):
    schema = client.get("/openapi.json").json()

    assert schema["paths"]["/tasks"]["post"]["tags"] == ["tasks"]
    assert schema["paths"]["/users/me"]["get"]["tags"] == ["users"]
    assert schema["paths"]["/admin/stats"]["get"]["tags"] == ["admin"]
