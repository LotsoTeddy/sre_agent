import chromadb
from volcenginesdkarkruntime import Ark

EMBEDDING_MODEL = "doubao-embedding-text-240715"


class KnowledgeBase:
    def __init__(
        self, collection_name: str = "test_chromadb_vectordb", data: list[str] = None
    ):
        self.collection_name = collection_name
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(collection_name)

        self.ark_client = Ark()
        response = self.ark_client.embeddings.create(model=EMBEDDING_MODEL, input=data)
        embeddings = [response.data[i].embedding for i in range(len(response.data))]

        self.collection.add(
            ids=[str(i) for i in range(len(data))],
            documents=data,
            embeddings=embeddings,
        )

    def search(self, query: str):
        """Retrieve documents similar to the query text in the vector database.

        Args:
            query (str): The query text to be retrieved (e.g., "Who proposed the Turing machine model?")

        Returns:
            list[str]: A list of the top most similar document contents retrieved (sorted by vector similarity)
        """

        # Request for embedding the input string to vector
        query_vector = self.ark_client.embeddings.create(
            model=EMBEDDING_MODEL, input=[query]
        )

        # Query the vector database with the embedding vector
        results = self.collection.query(
            query_embeddings=query_vector.data[0].embedding, n_results=20
        )
        return results["documents"]
