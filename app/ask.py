"""Lecture 01: a script that asks a bare LLM a single question.

Usage:
    uv run python -m app.ask "What is LoRA?"
    uv run python -m app.ask
    uv run python -m app.ask --chat
"""

import argparse

from google import genai
from google.genai import errors
from google.genai import types

from app.config import MODEL, api_error_message, get_api_key

DEFAULT_QUESTION = "What are the 3 homework levels in the AIE2026 course?"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
    )

    # Display token usage (Lecture 01 exercise)
    usage = response.usage_metadata

    if usage is not None:
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count

        print(
            f"[input tokens] "
            f"{input_tokens if input_tokens is not None else 'unknown'}"
        )
        print(
            f"[output tokens] "
            f"{output_tokens if output_tokens is not None else 'unknown'}"
        )
    else:
        print("[tokens] Usage metadata unavailable")

    return response.text


def chat() -> None:
    client = genai.Client(api_key=get_api_key())
    history: list[types.Content] = []

    while True:
        question = input("You: ")
        if question.strip().lower() in {"exit", "quit"}:
            break
        if not question.strip():
            continue

        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=question)],
        )
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[*history, user_message],
            )
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            continue

        answer = response.text or ""
        model_message = types.Content(
            role="model",
            parts=[types.Part.from_text(text=answer)],
        )
        history.extend((user_message, model_message))
        print(f"Gemini: {answer}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask a bare LLM a question"
    )
    question_group = parser.add_mutually_exclusive_group()
    question_group.add_argument(
        "question", nargs="?", default=DEFAULT_QUESTION
    )
    question_group.add_argument(
        "--chat",
        action="store_true",
        help="start an interactive conversation",
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")

    try:
        if args.chat:
            chat()
        else:
            print(f"[question] {args.question}\n")
            print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()