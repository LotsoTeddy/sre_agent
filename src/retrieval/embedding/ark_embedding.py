import os
import requests
import json
from src.retrieval.embedding.base_embedding import Embeddings


class ArkEmbeddings(Embeddings):
    def __init__(
            self,
            model: str = os.getenv("ARK_EMBEDDING_MODEL"),
            api_base: str = os.getenv("ARK_API_BASE"),
            api_key: str = os.getenv("ARK_API_KEY"),
    ):
        assert model is not None
        assert api_base is not None
        assert api_key is not None

        self.model = model  # data['model']
        self.url = api_base
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        data = {
            "model": self.model,
            "input": texts
        }
        response = requests.post(
            self.url,
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        return [item["embedding"] for item in result["data"]]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


