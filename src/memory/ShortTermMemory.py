from dataclasses import dataclass

from src.memory import BaseMemory


@dataclass
class ShortTermMemory(BaseMemory):
    """The short term memory is implemented by Chromadb."""

    def add(self, message: str):
        pass

    def search(self, query: str, top_k: int = 3):
        pass
