# Tasks and WebSocket Rooms API

Учебный FastAPI-проект с REST API задач, зависимостями, модульной маршрутизацией, Docker-контейнеризацией, WebSocket-комнатами и интеграционными тестами.

## Структура

```text
app/
  __init__.py
  main.py
  dependencies.py
  schemas.py
  storage.py
  room_manager.py
  routers/
    __init__.py
    tasks.py
    users.py
    admin.py
    rooms.py
tests/
  conftest.py
  test_tasks.py
  test_websocket.py
  test_dependencies_and_routing.py
  test_health.py
```

## Локальный запуск

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск приложения:

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Тесты

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Проверка API после запуска:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

Ожидаемый ответ для пустого списка:

```json
[]
```

Проверка health-route в Docker:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "env": "docker"
}
```

## Основные маршруты

### Tasks

Все маршруты `/tasks` требуют заголовок:

```text
X-User-Id: 10
```

Создание задачи:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 10" \
  -d '{"title":"Подготовить тесты","description":"Интеграционные тесты","status":"todo","priority":4}'
```

Получение задач текущего пользователя:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

Фильтрация:

```bash
curl "http://localhost:8000/tasks?status=todo&min_priority=4" -H "X-User-Id: 10"
```

### Users

```bash
curl http://localhost:8000/users/me -H "X-User-Id: 10"
```

### Admin

Админские маршруты требуют:

```text
X-User-Id: 1
X-User-Role: admin
```

Статистика:

```bash
curl http://localhost:8000/admin/stats -H "X-User-Id: 1" -H "X-User-Role: admin"
```

### WebSocket

Маршрут:

```text
/ws/rooms/{room_id}?username=alice
```

Пример JSON-сообщения:

```json
{
  "type": "message",
  "text": "Всем привет"
}
```

Если `username` отсутствует или пустой, сервер закрывает соединение с кодом `1008`.
