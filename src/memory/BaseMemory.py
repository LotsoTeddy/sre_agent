from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class BaseMemory:
    """The base memory is implemented by specific methods."""

    app_name: str
    user_id: str
    session_id: str

    @abstractmethod
    def add(self, message: str):
        pass

    @abstractmethod
    def search(self, query_embeddings: list, top_k: int = 3) -> list[str]:
        pass
