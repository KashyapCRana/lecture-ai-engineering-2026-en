"""Tests for the single-question and interactive ask CLI without API calls."""

import sys
from types import SimpleNamespace

from google.genai import errors

from app import ask as ask_module


class FakeModels:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def generate_content(self, *, model, contents):
        self.calls.append((model, list(contents) if isinstance(contents, list) else contents))
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result


def _response(text):
    return SimpleNamespace(text=text, usage_metadata=None)


def _text(message):
    return message.parts[0].text


def test_chat_sends_full_history_and_stops_on_exit(monkeypatch, capsys):
    models = FakeModels(
        [_response("First answer"), _response("Follow-up answer")]
    )
    monkeypatch.setattr(
        ask_module.genai,
        "Client",
        lambda **_: SimpleNamespace(models=models),
    )
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    questions = iter(["First question", "Follow-up question", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))
    monkeypatch.setattr(sys, "argv", ["app.ask", "--chat"])

    ask_module.main()

    assert len(models.calls) == 2
    first_history = models.calls[0][1]
    assert [(message.role, _text(message)) for message in first_history] == [
        ("user", "First question"),
    ]
    second_history = models.calls[1][1]
    assert [(message.role, _text(message)) for message in second_history] == [
        ("user", "First question"),
        ("model", "First answer"),
        ("user", "Follow-up question"),
    ]
    output = capsys.readouterr().out
    assert "Gemini: First answer" in output
    assert "Gemini: Follow-up answer" in output


def test_chat_api_error_does_not_change_successful_history(monkeypatch, capsys):
    models = FakeModels(
        [
            _response("First answer"),
            errors.APIError(429, {"error": {"message": "quota"}}),
            _response("Recovered answer"),
        ]
    )
    monkeypatch.setattr(
        ask_module.genai,
        "Client",
        lambda **_: SimpleNamespace(models=models),
    )
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    questions = iter(["First question", "Failed question", "Next question", "quit"])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    ask_module.chat()

    recovered_history = models.calls[2][1]
    assert [(message.role, _text(message)) for message in recovered_history] == [
        ("user", "First question"),
        ("model", "First answer"),
        ("user", "Next question"),
    ]
    assert "Rate limit reached." in capsys.readouterr().out


def test_single_question_behavior_and_token_display_are_unchanged(monkeypatch, capsys):
    usage = SimpleNamespace(prompt_token_count=12, candidates_token_count=7)
    models = FakeModels([SimpleNamespace(text="Answer", usage_metadata=usage)])
    monkeypatch.setattr(
        ask_module.genai,
        "Client",
        lambda **_: SimpleNamespace(models=models),
    )
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("Question") == "Answer"

    assert models.calls == [(ask_module.MODEL, "Question")]
    assert "[input tokens] 12" in capsys.readouterr().out
