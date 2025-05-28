from typing import Any

import chromadb

from src.retrieval.document import Document
from src.retrieval.vdb.vector import KnowledgeBaseVector, register_vector, VectorType


# from dotenv import load_dotenv
# load_dotenv()

@register_vector
class ChromaVector(KnowledgeBaseVector):
    name: str = VectorType.CHROMA.value

    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self._client = chromadb.Client()


    def create(self, texts: list[Document], **kwargs):
        # create
        self._client.get_or_create_collection(self._collection_name)
        # add text
        self.add_texts(texts)
        pass

    def add_texts(self, documents: list[Document], **kwargs):
        collection = self._client.get_or_create_collection(self._collection_name)
        collection.add(
            ids=[str(i) for i in range(len(documents))],
            documents=[document.page_content for document in documents],
            embeddings=[document.vector for document in documents],
        )
        pass

    def delete(self) -> None:
        pass

    def collection_exist(self) -> bool:
        pass

    def search_by_vector(self, query_vector: list[float], **kwargs: Any) -> list[str]:
        top_k = kwargs.get("top_k", 5)
        collection = self._client.get_or_create_collection(self._collection_name)
        results = collection.query(
            query_embeddings=query_vector,
            n_results=top_k
        )
        return results["documents"][0]

    def get_health(self):
        pass



