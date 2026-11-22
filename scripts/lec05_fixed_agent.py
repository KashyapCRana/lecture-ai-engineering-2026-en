"""Fixed-query answer evaluation for Lecture 05."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from pydantic_ai.exceptions import ModelHTTPError

from app import retrieval
from app.agent import agent, build_model, print_trace
from app.config import MODEL
from app.lec05_experiments import expand_adjacent_pages
from app.lec05_hybrid import select_hybrid

CASES_PATH = Path("lectures/05/eval_questions.json")
OUTPUT_PATH = Path("lectures/05/fixed_query_generation.jsonl")

VARIANTS = [
    "vector_only",
    "vector_adjacent",
    "hybrid",
    "hybrid_no_graph",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    case = next((c for c in cases if c["id"] == args.case), None)

    if case is None:
        parser.error(f"Unknown case: {args.case}")

    tool_runs = []

    def search_materials(query: str) -> str:
        """Search lecture materials and return grounded page evidence.

        Use query to specify what you want to look up.
        """
        fixed_query = case["query"]
        seeds = retrieval.search(fixed_query)

        if args.variant == "vector_only":
            selected = seeds

        elif args.variant == "vector_adjacent":
            selected = expand_adjacent_pages(
                seeds, retrieval.load_pages()
            )

        else:
            pages = retrieval.load_pages()
            tree = json.loads(
                retrieval.RAG_TREE.read_text(encoding="utf-8")
            )
            graph = json.loads(
                retrieval.RAG_GRAPH.read_text(encoding="utf-8")
            )

            selected = select_hybrid(
                fixed_query,
                seeds,
                pages,
                tree,
                graph,
                use_adjacent=True,
                use_tree=True,
                use_graph=args.variant == "hybrid",
                max_pages=10,
                max_chars=14000,
            )["results"]

        ids = [p["page_id"] for p in selected]

        tool_runs.append({
            "model_query": query,
            "fixed_query": fixed_query,
            "selected_ids": ids,
        })

        print("[retrieval] Fixed query:", fixed_query, flush=True)
        print("[retrieval] Selected:", ids, flush=True)

        return json.dumps(
            {"results": selected},
            ensure_ascii=False,
        )

    print("[model]", MODEL)
    print("[case]", case["id"])
    print("[variant]", args.variant)

    start = perf_counter()

    try:
        with agent.override(tools=[search_materials]):
            result = agent.run_sync(
                case["question"],
                model=build_model(),
            )

    except ModelHTTPError as exc:
        print("Model HTTP error:", exc.status_code)
        print(str(exc.body)[:300])
        raise SystemExit(1)

    elapsed = perf_counter() - start
    usage = result.usage

    record = {
        "case": case["id"],
        "category": case["category"],
        "variant": args.variant,
        "model": MODEL,
        "question": case["question"],
        "fixed_query": case["query"],
        "gold": case["gold"],
        "tool_runs": tool_runs,
        "answer": str(result.output),
        "elapsed_seconds": round(elapsed, 3),
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "model_responses": usage.requests,
        "estimated_cost_usd": (
            float(usage.cost)
            if usage.cost is not None else None
        ),
    }

    with OUTPUT_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("\n--- ANSWER ---")
    print(result.output)

    if args.trace:
        print_trace(result, elapsed)

    print("[saved]", OUTPUT_PATH)


if __name__ == "__main__":
    main()
