from starlette.websockets import WebSocketDisconnect


def test_connect_to_room_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        event = websocket.receive_json()
        assert event["type"] == "join"
        assert event["room_id"] == "python"
        assert event["username"] == "alice"


def test_connect_to_room_without_username_is_rejected(client):
    try:
        with client.websocket_connect("/ws/rooms/python"):
            raise AssertionError("Connection without username should not be accepted")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_send_message_and_receive_response(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()  # join event
        websocket.send_json({"type": "message", "text": "Всем привет"})

        event = websocket.receive_json()
        assert event == {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Всем привет",
        }


def test_two_clients_in_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()  # alice joined
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            bob_join = bob.receive_json()
            alice_join_about_bob = alice.receive_json()
            assert bob_join["type"] == "join"
            assert alice_join_about_bob["username"] == "bob"

            alice.send_json({"type": "message", "text": "hello"})

            expected = {
                "type": "message",
                "room_id": "python",
                "username": "alice",
                "text": "hello",
            }
            assert alice.receive_json() == expected
            assert bob.receive_json() == expected


def test_users_from_different_rooms_do_not_receive_foreign_messages(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/js?username=bob") as bob:
            bob.receive_json()

            alice.send_json({"type": "message", "text": "python only"})
            assert alice.receive_json()["room_id"] == "python"

            bob.send_json({"type": "message", "text": "js only"})
            bob_event = bob.receive_json()
            assert bob_event == {
                "type": "message",
                "room_id": "js",
                "username": "bob",
                "text": "js only",
            }


def test_long_message_returns_error_to_sender(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "x" * 301})

        event = websocket.receive_json()
        assert event == {"type": "error", "detail": "Message is too long"}


def test_disconnected_user_is_removed_from_room_users(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        response_inside = client.get("/rooms/python/users")
        assert response_inside.json() == {"room_id": "python", "users": ["alice"]}

    response_after = client.get("/rooms/python/users")
    assert response_after.json() == {"room_id": "python", "users": []}
