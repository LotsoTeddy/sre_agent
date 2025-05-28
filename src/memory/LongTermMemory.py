from dataclasses import dataclass

from src.memory import BaseMemory


@dataclass
class LongTermMemory(BaseMemory):
    def add(self, message: str):
        pass

    def search(self, query: str, top_k: int = 3):
        pass
