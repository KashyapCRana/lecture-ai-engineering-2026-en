"""Controlled retrieval ablations for Lecture 05."""

import json
from pathlib import Path

from app import retrieval
from app.lec05_hybrid import select_hybrid


QUESTIONS = [
    {
        "id": "lora",
        "query": "LoRA freeze train QLoRA add",
        "gold": ["lec02-main-p052"],
    },
    {
        "id": "memory",
        "query": "compaction memory sessions lecture 03 daily notes long-term memory",
        "gold": [
            "lec03-main-p013",
            "lec03-main-p039",
            "lec03-main-p040",
            "lec03-main-p065",
        ],
    },
    {
        "id": "unanswerable",
        "query": "average response time and accuracy of the RAG system built in the lecture",
        "gold": [],
    },
]

VARIANTS = {
    "vector_only": (False, False, False),
    "vector_adjacent": (True, False, False),
    "vector_tree": (False, True, False),
    "vector_graph": (False, False, True),
    "hybrid": (True, True, True),
    "hybrid_no_adjacent": (False, True, True),
    "hybrid_no_tree": (True, False, True),
    "hybrid_no_graph": (True, True, False),
}

MAX_PAGES = 10
MAX_CHARS = 14000


def main():
    pages = retrieval.load_pages()
    tree = json.loads(retrieval.RAG_TREE.read_text(encoding="utf-8"))
    graph = json.loads(retrieval.RAG_GRAPH.read_text(encoding="utf-8"))

    records = []

    for question in QUESTIONS:
        print(f"\nQUESTION: {question['id']}", flush=True)

        # Same search seeds for every variant of this question.
        seeds = retrieval.search(question["query"])
        seed_ids = [p["page_id"] for p in seeds]

        for name, (adjacent, use_tree, use_graph) in VARIANTS.items():
            result = select_hybrid(
                question["query"],
                seeds,
                pages,
                tree,
                graph,
                use_adjacent=adjacent,
                use_tree=use_tree,
                use_graph=use_graph,
                max_pages=MAX_PAGES,
                max_chars=MAX_CHARS,
            )

            selected_ids = [
                p["page_id"] for p in result["results"]
            ]
            gold = set(question["gold"])
            found = sorted(gold & set(selected_ids))

            record = {
                "question": question["id"],
                "query": question["query"],
                "variant": name,
                "seed_ids": seed_ids,
                "selected_ids": selected_ids,
                "gold_ids": sorted(gold),
                "gold_found": found,
                "gold_recall": (
                    len(found) / len(gold) if gold else None
                ),
                "candidate_count": result["candidate_count"],
                "selected_count": len(selected_ids),
                "context_chars": result["context_chars"],
                "max_chars": MAX_CHARS,
                "max_pages": MAX_PAGES,
            }
            records.append(record)

            coverage = (
                f"{len(found)}/{len(gold)}"
                if gold else "N/A"
            )

            print(
                f"{name:20s} "
                f"pages={len(selected_ids):2d} "
                f"candidates={result['candidate_count']:3d} "
                f"chars={result['context_chars']:5d} "
                f"gold={coverage}"
            )

            assert result["context_chars"] <= MAX_CHARS
            assert len(selected_ids) == len(set(selected_ids))

    output = Path("lectures/05/retrieval_ablation.json")
    output.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nSaved {len(records)} records to {output}")


if __name__ == "__main__":
    main()
