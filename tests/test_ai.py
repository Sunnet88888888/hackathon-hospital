def test_audio_transcription_endpoint_returns_openai_transcript(client, monkeypatch, admin_headers):
    from app.config import settings
    from app.routes import ai

    captured = {}

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