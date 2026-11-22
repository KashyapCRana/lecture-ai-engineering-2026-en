"""Lecture 05 Advanced: hybrid vector, tree, and graph retrieval."""

import json
import re
from collections import defaultdict, deque

from app import retrieval
from app.lec05_experiments import expand_adjacent_pages

STOP = {
    "the", "and", "for", "what", "how", "does", "are",
    "from", "with", "into", "that", "this", "which",
    "about", "lecture", "between", "when",
}


def terms(text):
    return {
        word for word in re.findall(r"[a-z0-9]+", text.lower())
        if len(word) > 2 and word not in STOP
    }


def select_hybrid(
    query, seeds, pages, tree, graph, *,
    use_adjacent=True,
    use_tree=True,
    use_graph=True,
    max_pages=10,
    max_chars=14000,
):
    """Rank structural evidence and enforce a serialized context budget."""
    if max_pages < 1 or max_chars < 100:
        raise ValueError("Invalid retrieval budget")

    by_id = {page["page_id"]: page for page in pages}
    query_terms = terms(query)
    candidates = {}

    def add(pid, source, rank=0, hops=0):
        if pid not in by_id:
            return

        entry = candidates.setdefault(pid, {
            "page": by_id[pid],
            "sources": set(),
            "base_score": -1000,
        })
        entry["sources"].add(source)

        base = {
            "vector": 100 - 8 * rank,
            "adjacent": 42,
            "tree": 40,
            "graph": 43 - 4 * hops,
        }[source]

        entry["base_score"] = max(entry["base_score"], base)

        if source == "vector":
            entry["distance"] = seeds[rank].get("distance")

    # A: original vector candidates.
    for rank, seed in enumerate(seeds):
        add(seed["page_id"], "vector", rank=rank)

    # B: neighboring pages, bounded within each document.
    if use_adjacent:
        expanded = expand_adjacent_pages(seeds, pages)
        for page in expanded:
            if page["retrieval_role"] == "adjacent":
                add(page["page_id"], "adjacent")

    # C: pages belonging to the same Tree section.
    if use_tree:
        siblings = {}

        def walk(node):
            if node.get("kind") == "section":
                ids = [
                    child["id"]
                    for child in node.get("children", [])
                    if child.get("kind") == "page"
                    and child["id"] in by_id
                ]
                for pid in ids:
                    siblings[pid] = ids

            for child in node.get("children", []):
                walk(child)

        walk(tree)

        for seed in seeds:
            seed_id = seed["page_id"]
            related = [
                pid for pid in siblings.get(seed_id, [])
                if pid != seed_id
            ]
            related.sort(key=lambda pid: (
                -len(query_terms & terms(
                    by_id[pid]["title"] + " " + by_id[pid]["content"]
                )),
                abs(by_id[pid]["page"] - seed["page"]),
                pid,
            ))
            for pid in related[:2]:
                add(pid, "tree")

    # D: bounded Graph traversal, including page-term-page paths.
    if use_graph:
        valid_nodes = {
            node["id"]
            for node in graph["nodes"]
            if node["kind"] == "term" or node["id"] in by_id
        }
        adjacent = defaultdict(set)

        for edge in graph["edges"]:
            a, b = edge["source"], edge["target"]
            if (
                edge["relation"] in ("next_page", "mentions")
                and a in valid_nodes
                and b in valid_nodes
            ):
                adjacent[a].add(b)
                adjacent[b].add(a)

        for seed in seeds[:3]:
            root = seed["page_id"]
            visited = {root}
            queue = deque([(root, 0)])

            while queue and len(visited) < 80:
                current, hops = queue.popleft()
                if hops >= 2:
                    continue

                neighbors = sorted(
                    adjacent[current],
                    key=lambda pid: (len(adjacent[pid]), pid),
                )

                for neighbor in neighbors:
                    if neighbor in visited:
                        continue
                    if len(visited) >= 80:
                        break

                    visited.add(neighbor)
                    queue.append((neighbor, hops + 1))

                    if neighbor in by_id and neighbor != root:
                        add(neighbor, "graph", hops=hops + 1)

    # E: rank candidates using vector priority, lexical relevance,
    # and agreement across retrieval methods.
    ranked = []

    for pid, entry in candidates.items():
        page = entry["page"]
        searchable = (
            page["title"] + " " +
            page["section"] + " " +
            page["content"]
        )
        overlap = len(query_terms & terms(searchable))
        title_overlap = len(query_terms & terms(page["title"]))

        score = (
            entry["base_score"]
            + min(24, 4 * overlap)
            + 12 * title_overlap
            + 6 * (len(entry["sources"]) - 1)
        )

        result = {
            **page,
            "retrieval_sources": sorted(entry["sources"]),
            "retrieval_score": score,
        }

        if "distance" in entry and entry["distance"] is not None:
            result["distance"] = entry["distance"]

        ranked.append((score, overlap, pid, result))

    ranked.sort(key=lambda x: (-x[0], -x[1], x[2]))

    # F: enforce the actual serialized character limit.
    selected = []

    def context_size(items):
        return len(json.dumps({"results": items}, ensure_ascii=False))

    for _, _, _, result in ranked:
        if len(selected) >= max_pages:
            break
        if context_size(selected + [result]) <= max_chars:
            selected.append(result)

    return {
        "results": selected,
        "candidate_count": len(candidates),
        "context_chars": context_size(selected),
        "max_context_chars": max_chars,
    }


def hybrid_search(query, **kwargs):
    """One vector search, followed by local structural expansion."""
    seeds = retrieval.search(query)
    pages = retrieval.load_pages()
    tree = json.loads(retrieval.RAG_TREE.read_text(encoding="utf-8"))
    graph = json.loads(retrieval.RAG_GRAPH.read_text(encoding="utf-8"))

    return select_hybrid(
        query, seeds, pages, tree, graph, **kwargs
    )
