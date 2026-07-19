from typing import List, TypedDict


class Item(TypedDict, total=False):
    title: str
    url: str
    summary: str
    source: str
    category: str
    published: str
    ai_summary: str
    name: str
    description: str
    abstract: str
    authors: List[str]
    stars: int
    language: str
    topics: List[str]
    score: int
    votes: int
    points: int
    comments: int
    full_text: str
    tagline: str
    implemented_by: dict
    is_correlated: bool


class Subscriber(TypedDict, total=False):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: str
    confirmed_at: str
    token: str


class TokenUsage(TypedDict, total=False):
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
