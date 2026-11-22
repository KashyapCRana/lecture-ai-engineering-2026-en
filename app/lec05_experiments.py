"""Lecture 05 experimental retrieval compatibility wrappers."""

from app import retrieval
from app.retrieval import expand_adjacent_pages


def search_with_adjacent_pages(query: str, radius: int = 1):
    return retrieval.search_with_adjacent_pages(query, radius)
