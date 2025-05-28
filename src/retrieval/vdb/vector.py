from abc import ABC, abstractmethod
from src.retrieval.document.document import Document
from typing import Any, Type
from enum import Enum


class KnowledgeBaseVector(ABC):
    name: str
    def __init__(
            self,
            collection_name: str
    ):
        self._collection_name = collection_name.lower()

    @abstractmethod
    def create(self, texts: list[Document], **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add_texts(self, documents: list[Document], **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def collection_exist(self) -> bool:
        raise NotImplementedError

    @property
    def collection_name(self):
        return self._collection_name
    @abstractmethod
    def search_by_vector(self, query_vector: list[float], **kwargs: Any) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_health(self):
        raise NotImplementedError


CLS_TO_VECTOR = dict()


def register_vector(cls: Type[KnowledgeBaseVector]):
    CLS_TO_VECTOR[cls.name] = cls
    return cls


def generate_vector(name: str, collection_name: str) -> KnowledgeBaseVector:
    return CLS_TO_VECTOR[name](collection_name)


class VectorType(Enum):
    ELASTICSEARCH = 'elasticsearch'
    OPENSEARCH = 'opensearch'
    CHROMA = 'chroma'