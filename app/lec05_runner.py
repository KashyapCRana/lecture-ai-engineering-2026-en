"""Run Lecture 05 adjacent-page retrieval experiments."""

import argparse
import json
import sqlite3
from time import perf_counter

from google.genai.errors import APIError
from pydantic_ai.exceptions import ModelHTTPError

from app.agent import agent, build_model, print_trace
from app.config import MODEL, api_error_message
from app.lec05_experiments import search_with_adjacent_pages


def search_materials(query: str) -> str:
    """Search the main materials for Lectures 01–03 and return relevant page text, titles, and page numbers.

    Use query to specify what you want to look up.
    """
    try:
        results = search_with_adjacent_pages(query)
        print(f"[retrieval] Returned {len(results)} unique pages")
        for page in results:
            print(
                f"  {page['page_id']} "
                f"({page['retrieval_role']})"
            )
        return json.dumps({"results": results}, ensure_ascii=False)

    except (ValueError, FileNotFoundError, sqlite3.Error) as exc:
        return json.dumps({"error": str(exc), "results": []})

    except APIError as exc:
        return json.dumps({
            "error": api_error_message(exc.code),
            "results": [],
        })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print("[method] Adjacent-page retrieval, radius=1")

    start = perf_counter()

    try:
        with agent.override(tools=[search_materials]):
            result = agent.run_sync(
                args.question,
                model=build_model(),
            )
    except ModelHTTPError as exc:
        print(api_error_message(exc.status_code, str(exc.body)[:200]))
        raise SystemExit(1)

    elapsed = perf_counter() - start
    print(result.output)

    if args.trace:
        print_trace(result, elapsed)


if __name__ == "__main__":
    main()
