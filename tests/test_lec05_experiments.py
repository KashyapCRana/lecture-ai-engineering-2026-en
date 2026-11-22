import pytest

from app.lec05_experiments import expand_adjacent_pages


def page(doc, n):
    return {
        "page_id": f"{doc}-p{n:03d}",
        "document_id": doc,
        "page": n,
        "title": f"Page {n}",
        "content": f"Text {n}",
        "citation": f"PDF p.{n}",
    }


def test_adjacent_expansion_and_deduplication():
    pages = [page("lec01-main", n) for n in range(1, 5)]
    hits = [
        {**pages[1], "distance": 0.1},
        {**pages[2], "distance": 0.2},
    ]

    result = expand_adjacent_pages(hits, pages)
    ids = [p["page_id"] for p in result]

    assert ids == [
        "lec01-main-p002",
        "lec01-main-p003",
        "lec01-main-p001",
        "lec01-main-p004",
    ]
    assert len(ids) == len(set(ids))
    assert all("citation" in p for p in result)
    assert result[0]["retrieval_role"] == "seed"
    assert result[2]["retrieval_role"] == "adjacent"


def test_document_boundary():
    pages = [
        page("lec01-main", 1),
        page("lec02-main", 1),
    ]

    result = expand_adjacent_pages([pages[0]], pages)
    assert len(result) == 1
    assert result[0]["document_id"] == "lec01-main"


def test_invalid_radius():
    with pytest.raises(ValueError):
        expand_adjacent_pages([], [], radius=-1)
