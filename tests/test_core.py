"""No live Gemini calls. These exercises check UI-independent behavior."""
from io import BytesIO
from unittest.mock import patch
import sys
import types

import pytest
from docx import Document

from core import (
    MAX_AUDIO_BYTES, UsageLimiter, UserFacingError, clean_title,
    generate_notes, printable_html, to_docx, transcribe_audio, validate_audio,
)


class FakeFile:
    name = "files/mock123"


class FakeFiles:
    def __init__(self):
        self.uploaded = False
        self.deleted = []

    def upload(self, file, config):
        self.uploaded = True
        return FakeFile()

    def delete(self, name):
        self.deleted.append(name)


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    def __init__(self, response):
        self.response = response
        self.last_call = None

    def generate_content(self, **kwargs):
        self.last_call = kwargs
        return FakeResponse(self.response)


class FakeClient:
    def __init__(self, response):
        self.files = FakeFiles()
        self.models = FakeModels(response)


def test_audio_formats_validation():
    assert validate_audio("recording.MP3", b"data")[1] == "audio/mpeg"
    for name, content in [("virus.exe", b"a"), ("lecture.wav", b""), ("clip.mp3", b"x" * (MAX_AUDIO_BYTES + 1))]:
        with pytest.raises(UserFacingError):
            validate_audio(name, content)


def test_transcribe_mocked_upload_delete():
    # Stub the types import so the tests don't require real Gemini service access.
    genai = types.ModuleType("google.genai")
    types_mod = types.ModuleType("google.genai.types")
    types_mod.UploadFileConfig = lambda **kwargs: kwargs
    client = FakeClient("අද අපි database එක ගැන ඉගෙන ගනිමු.")
    with patch.dict(sys.modules, {"google.genai": genai, "google.genai.types": types_mod}):
        result = transcribe_audio("x", b"example", "lecture.m4a", client=client)
    assert "database" in result
    assert client.files.uploaded
    assert client.files.deleted == ["files/mock123"]


def test_generate_notes_safe_prompt():
    client = FakeClient("# සාරාංශය\n- Database")
    result = generate_notes("notused", "This lecture introduces database tables and primary keys", "DB", "IT", client=client)
    assert "සාරාංශය" in result
    assert "untrusted" in client.models.last_call["config"]["system_instruction"].lower()
    with pytest.raises(UserFacingError):
        generate_notes("x", "short", "T", "S", client=client)


def test_sinhala_docx():
    file = to_docx("විෂය", "දත්ත", "මේක transcript එක", "## සාරාංශය\n- වැදගත් කරුණ")
    doc = Document(BytesIO(file))
    text = " ".join(paragraph.text for paragraph in doc.paragraphs)
    assert "සාරාංශය" in text and "වැදගත්" in text and "දත්ත" in text


def test_html_safe_and_utf8():
    text = printable_html("<script>x</script>", "IT", "<script>evil()</script>", "# සාරාංශය\n- ලක්ෂණ")
    output = text.decode("utf-8")
    assert "&lt;script&gt;" in output
    assert "<script>" not in output
    assert "සාරාංශය" in output
    assert "window.print()" in output


def test_limiter():
    limit = UsageLimiter(per_hour=2, per_day=3)
    assert limit.reserve(now=100000)[0]
    assert limit.reserve(now=100001)[0]
    assert not limit.reserve(now=100002)[0]
    assert limit.reserve(now=103601)[0]
    assert not limit.reserve(now=103602)[0]
    assert limit.reserve(now=200001)[0]


def test_clean_title():
    assert clean_title("  Hello  World\n ") == "Hello World"
    assert clean_title(" ") == "Untitled lecture"
