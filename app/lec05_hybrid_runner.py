"""Run the Lecture 05 Advanced hybrid RAG agent."""

import argparse
import json
from time import perf_counter

from pydantic_ai.exceptions import ModelHTTPError

from app.agent import agent, build_model, print_trace
from app.config import MODEL, api_error_message
from app.lec05_hybrid import hybrid_search


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--max-chars", type=int, default=14000)
    parser.add_argument("--no-adjacent", action="store_true")
    parser.add_argument("--no-tree", action="store_true")
    parser.add_argument("--no-graph", action="store_true")
    args = parser.parse_args()

    def search_materials(query: str) -> str:
        """Search the main lecture materials for relevant evidence.

        Use query to specify what you want to look up.
        Return page text and citation metadata.
        """
        result = hybrid_search(
            query,
            use_adjacent=not args.no_adjacent,
            use_tree=not args.no_tree,
            use_graph=not args.no_graph,
            max_pages=args.max_pages,
            max_chars=args.max_chars,
        )

        lines = [
            f"[hybrid] Query: {query}",
            f"[hybrid] Candidates: {result['candidate_count']}",
            f"[hybrid] Selected: {len(result['results'])}",
            f"[hybrid] Context chars: {result['context_chars']}",
        ]

        for page in result["results"]:
            lines.append(
                f"  {page['page_id']} "
                f"score={page['retrieval_score']} "
                f"sources={','.join(page['retrieval_sources'])}"
            )

        print("\n".join(lines), flush=True)

        return json.dumps(
            {"results": result["results"]},
            ensure_ascii=False,
        )

    print(f"[model] {MODEL}")
    print("[method] Advanced hybrid RAG")

    start = perf_counter()

    try:
        with agent.override(tools=[search_materials]):
            result = agent.run_sync(
                args.question,
                model=build_model(),
            )
    except ModelHTTPError as exc:
        print(
            api_error_message(
                exc.status_code,
                str(exc.body)[:200],
            )
        )
        raise SystemExit(1)

    elapsed = perf_counter() - start
    print(result.output)

    if args.trace:
        print_trace(result, elapsed)


if __name__ == "__main__":
    main()
