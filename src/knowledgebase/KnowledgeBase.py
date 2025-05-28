from dataclasses import dataclass


@dataclass
class KnowledgeBase:
    name: str
    collection: str

    def add(self, documents: list[str]):
        pass

    def search(self, query: str, top_k: int = 3) -> list[str]:
        pass
