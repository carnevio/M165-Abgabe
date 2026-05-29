from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Joke:
    text: str
    category: list[str] = field(default_factory=list)
    author: str = ""

    def to_document(self) -> dict:
        return {
            "text": self.text,
            "category": list(self.category),
            "author": self.author,
        }

    @classmethod
    def from_document(cls, document: dict) -> "Joke":
        categories = document.get("category", [])
        if not isinstance(categories, list):
            categories = [str(categories)]

        return cls(
            text=str(document.get("text", "")),
            category=[str(item) for item in categories],
            author=str(document.get("author", "")),
        )
