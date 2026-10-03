def test_audio_transcription_endpoint_returns_openai_transcript(client, monkeypatch, admin_headers):
    from app.config import settings
    from app.routes import ai

    captured = {}

    def test_conversation_lifecycle_is_authenticated_and_user_scoped(client, admin_headers, monkeypatch):
        from app.routes import ai

        agent_calls = []

        async def fake_ai_runner(*, user_token, context):
            agent_calls.append((user_token, context))
            return f"Ответ {len(agent_calls)}"

        monkeypatch.setattr(ai, "ai_runner", fake_ai_runner)
        token = admin_headers["Authorization"].removeprefix("Bearer ")

        create_response = client.post(
            "/conversations",
            json={"message": "Первое сообщение"},
            headers=admin_headers,
        )
        assert create_response.status_code == 201
        conversation = create_response.json()["conversation"]
        conversation_id = conversation["id"]
        assert [message["role"] for message in conversation["messages"]] == ["user", "assistant"]
        assert conversation["messages"][1]["content"] == "Ответ 1"
        assert agent_calls[0] == (
            token,
            [{"role": "user", "content": "Первое сообщение"}],
        )

        send_response = client.post(
            f"/conversations/{conversation_id}/messages",
            json={"content": "Продолжение"},
            headers=admin_headers,
        )
        assert send_response.status_code == 201
        assert send_response.json()["assistant_message"]["content"] == "Ответ 2"
        assert [message["role"] for message in agent_calls[1][1]] == [
            "user", "assistant", "user"
        ]

        list_response = client.get("/conversations", headers=admin_headers)
        assert list_response.status_code == 200
        assert [item["id"] for item in list_response.json()] == [conversation_id]

        detail_response = client.get(f"/conversations/{conversation_id}", headers=admin_headers)
        assert detail_response.status_code == 200
        assert len(detail_response.json()["messages"]) == 4

        client.post("/auth/register", json={
            "email": "another-patient@clinic.com",
            "password": "patientpassword123",
            "full_name": "Another Patient",
            "role": "patient",
        })
        other_login = client.post("/auth/login", json={
            "email": "another-patient@clinic.com",
            "password": "patientpassword123",
        })
        other_headers = {
            "Authorization": f"Bearer {other_login.json()['access_token']}"
        }
        assert client.get(f"/conversations/{conversation_id}", headers=other_headers).status_code == 404

        delete_response = client.delete(f"/conversations/{conversation_id}", headers=admin_headers)
        assert delete_response.status_code == 204
        assert client.get(f"/conversations/{conversation_id}", headers=admin_headers).status_code == 404
    class FakeTranscriptions:
        async def create(self, *, model, file, response_format, language):
            captured["model"] = model
            captured["filename"] = file[0]
            captured["audio"] = file[1].read()
            captured["response_format"] = response_format
            captured["language"] = language
            return "Распознанный текст"

    class FakeClient:
        def __init__(self, *, api_key):
            assert api_key == "test-openai-key"
            self.audio = type("Audio", (), {"transcriptions": FakeTranscriptions()})()

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setattr(ai, "AsyncOpenAI", FakeClient)
    response = client.post(
        "/ai/convert_audio_to_text",
        files={"file": ("sample.wav", b"audio data", "audio/wav")},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == {"text": "Распознанный текст"}
    assert captured == {
        "model": "whisper-1",
        "filename": "sample.wav",
        "audio": b"audio data",
        "response_format": "text",
        "language": "ru",
    }


def test_audio_transcription_requires_api_key(client, monkeypatch, admin_headers):
    from app.config import settings

    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    response = client.post(
        "/ai/convert_audio_to_text",
        files={"file": ("sample.wav", b"audio data", "audio/wav")},
        headers=admin_headers,
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Audio transcription is not configured."


def test_audio_transcription_requires_authentication(client):
    response = client.post(
        "/ai/convert_audio_to_text",
        files={"file": ("sample.wav", b"audio data", "audio/wav")},
    )

    assert response.status_code == 401