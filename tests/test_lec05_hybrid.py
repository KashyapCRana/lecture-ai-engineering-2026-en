import json

from app.lec05_hybrid import select_hybrid


def make_data():
    pages = [
        {
            "page_id": f"lec01-main-p{i:03d}",
            "document_id": "lec01-main",
            "lecture": 1,
            "document_title": "Test Lecture",
            "section": "Test Section",
            "title": f"Topic page {i}",
            "page": i,
            "content": f"Evidence from page {i}.",
            "citation": f"Lecture 1, p.{i}",
        }
        for i in range(1, 6)
    ]

    def node(page):
        return {
            "id": page["page_id"],
            "kind": "page",
            "title": page["title"],
        }

    tree = {
        "id": "root",
        "kind": "collection",
        "title": "Course",
        "children": [{
            "id": "lec01-main",
            "kind": "document",
            "title": "Test Lecture",
            "children": [
                {
                    "id": "section-a",
                    "kind": "section",
                    "title": "Section A",
                    "children": [node(p) for p in pages[:3]],
                },
                {
                    "id": "section-b",
                    "kind": "section",
                    "title": "Section B",
                    "children": [node(p) for p in pages[3:]],
                },
            ],
        }],
    }

    graph = {
        "nodes": [
            *[node(p) for p in pages],
            {"id": "term:shared", "kind": "term", "title": "shared"},
        ],
        "edges": [
            {
                "source": pages[1]["page_id"],
                "target": "term:shared",
                "relation": "mentions",
            },
            {
                "source": pages[4]["page_id"],
                "target": "term:shared",
                "relation": "mentions",
            },
        ],
    }

    seeds = [{**pages[1], "distance": 0.1}]
    return seeds, pages, tree, graph


def run(**options):
    seeds, pages, tree, graph = make_data()
    return select_hybrid(
        "topic evidence",
        seeds,
        pages,
        tree,
        graph,
        max_pages=10,
        max_chars=10000,
        **options,
    )


def ids(result):
    return {p["page_id"] for p in result["results"]}


def test_vector_only():
    result = run(
        use_adjacent=False,
        use_tree=False,
        use_graph=False,
    )
    assert ids(result) == {"lec01-main-p002"}


def test_adjacent_only():
    result = run(
        use_adjacent=True,
        use_tree=False,
        use_graph=False,
    )
    assert ids(result) == {
        "lec01-main-p001",
        "lec01-main-p002",
        "lec01-main-p003",
    }


def test_tree_only():
    result = run(
        use_adjacent=False,
        use_tree=True,
        use_graph=False,
    )
    assert ids(result) == {
        "lec01-main-p001",
        "lec01-main-p002",
        "lec01-main-p003",
    }


def test_graph_only():
    result = run(
        use_adjacent=False,
        use_tree=False,
        use_graph=True,
    )
    assert "lec01-main-p005" in ids(result)
    assert "graph" in next(
        p["retrieval_sources"]
        for p in result["results"]
        if p["page_id"] == "lec01-main-p005"
    )


def test_hybrid_deduplication():
    result = run()
    page_ids = [p["page_id"] for p in result["results"]]
    assert len(page_ids) == len(set(page_ids))
    assert "lec01-main-p005" in page_ids


def test_budget_enforcement():
    result = run()
    assert result["context_chars"] <= result["max_context_chars"]
    assert len(result["results"]) <= 10

    first = result["results"][0]
    limit = len(json.dumps(
        {"results": [first]},
        ensure_ascii=False,
    ))

    seeds, pages, tree, graph = make_data()

    limited = select_hybrid(
        "topic evidence",
        seeds,
        pages,
        tree,
        graph,
        max_pages=10,
        max_chars=limit,
    )

    assert len(limited["results"]) == 1
    assert limited["context_chars"] <= limit
