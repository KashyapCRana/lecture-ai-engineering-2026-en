"""Q06 retrieval comparison with measured Gemini token caps."""

import json
from functools import lru_cache
from pathlib import Path

from google import genai

from app import retrieval
from app.config import MODEL, get_api_key
from app.lec05_experiments import expand_adjacent_pages
from app.lec05_hybrid import select_hybrid


def main():
    cases = json.loads(
        Path("lectures/05/eval_questions.json").read_text()
    )
    case = next(q for q in cases if q["id"] == "Q06")

    # One vector retrieval shared across every configuration.
    seeds = retrieval.search(case["query"])
    pages = retrieval.load_pages()
    tree = json.loads(retrieval.RAG_TREE.read_text())
    graph = json.loads(retrieval.RAG_GRAPH.read_text())

    variants = {
        "vector_only": seeds,
        "vector_adjacent": expand_adjacent_pages(seeds, pages),
    }

    for name, enable_graph in [
        ("hybrid", True),
        ("hybrid_no_graph", False),
    ]:
        result = select_hybrid(
            case["query"], seeds, pages, tree, graph,
            use_graph=enable_graph,
            max_pages=10,
            max_chars=14000,
        )
        variants[name] = result["results"]

    records = []
    gold = set(case["gold"])

    def payload(items):
        return json.dumps({"results": items}, ensure_ascii=False)

    with genai.Client(api_key=get_api_key()) as client:

        @lru_cache(maxsize=None)
        def count_tokens(serialized):
            result = client.models.count_tokens(
                model=MODEL,
                contents=serialized,
            )
            if result.total_tokens is None:
                raise ValueError("Token count unavailable")
            return result.total_tokens

        def select_under_budget(items, budget):
            # Keep the longest ranked prefix that fits.
            low, high = 0, len(items)

            while low < high:
                middle = (low + high + 1) // 2
                current = items[:middle]

                if count_tokens(payload(current)) <= budget:
                    low = middle
                else:
                    high = middle - 1

            selected = items[:low]
            actual_tokens = count_tokens(payload(selected))

            assert actual_tokens <= budget
            return selected, actual_tokens

        for budget in [1600, 2200, 3200]:
            print(f"\n=== Budget: {budget} tokens ===")

            for name, ranked in variants.items():
                selected, actual = select_under_budget(
                    ranked, budget
                )

                selected_ids = [
                    p["page_id"] for p in selected
                ]
                found = sorted(gold & set(selected_ids))
                missing = sorted(gold - set(selected_ids))

                record = {
                    "case": "Q06",
                    "model": MODEL,
                    "variant": name,
                    "budget": budget,
                    "actual_retrieval_tokens": actual,
                    "selected_ids": selected_ids,
                    "gold_found": found,
                    "gold_missing": missing,
                    "gold_recall": len(found) / len(gold),
                }
                records.append(record)

                print(
                    f"{name:20s} "
                    f"pages={len(selected):2d} "
                    f"tokens={actual:4d} "
                    f"evidence={len(found)}/{len(gold)}"
                )

                if missing:
                    print("  Missing:", missing)

    output = Path("lectures/05/token_budget_q06.json")
    output.write_text(
        json.dumps(records, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nSaved {len(records)} records to {output}")


if __name__ == "__main__":
    main()
