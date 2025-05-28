from dotenv import load_dotenv
load_dotenv()

from dataclasses import dataclass

from src.memory import BaseMemory
from src.retrieval.vdb import ChromaVector, generate_vector,VectorType
from src.retrieval.embedding import ArkEmbeddings
from src.retrieval.document import Document


@dataclass
class ShortTermMemory(BaseMemory):
    """The short term memory is implemented by Chromadb."""
    def __init__(
        self,
        app_name: str,
        user_id: str,
        session_id: str
    ):
        super().__init__(app_name=app_name, user_id=user_id, session_id=session_id)
        self._vector = generate_vector(VectorType.CHROMA.value, collection_name="shot_term_memory")
        self._embedding = ArkEmbeddings()

    def add(self, message: str):

        self._vector.create(
            texts=[
                Document(
                    page_content=message,
                    vector=self._embedding.embed_query(message)
                )
            ]
        )
        pass

    def search(self, query: str, top_k: int = 3) -> list[str]:
        result = self._vector.search_by_vector(
            query_vector=self._embedding.embed_query(query)
        )
        return result


if __name__ == "__main__":
    # test code
    # python src/memory/ShortTermMemory.py
    s = ShortTermMemory(
        app_name="shot_term_memory",
        user_id="shot_term_memory",
        session_id="shot_term_memory",
    )
    s.add("今天是星期四，V我50")
    s.add("昨天是星期三")
    s.add("明天是星期五")
    print(s.search("今天是周几?"))