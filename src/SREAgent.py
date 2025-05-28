from src.knowledgebase import KnowledgeBase
from src.memory import LongTermMemory, ShortTermMemory


class SREAgent:
    def __init__(
        self,
        model: str,
        name: str,
        description: str,
        instruction: str,
        tools: list,
        knowledgebase: KnowledgeBase,
        short_term_memory: ShortTermMemory,
        long_term_memory: LongTermMemory,
    ):
        self.agent = None
        self.description = None
        self.instruction = None

        self.tools = None

        self.knowledgebase = None

        self.short_term_memory = None
        self.long_term_memory = None

    def run(self, prompt: str):
        documents = self.search(prompt)
        messages = []

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """We obey the following RAG flow:
        1. Search long-term memory
        2. Search short-term memory
        3. Search knowledgebase
        """
        embeded_query = []
        documents = []

        if self.short_term_memory is not None:
            res = self.short_term_memory.search(embeded_query, top_k)
            documents.extend(res)

        if self.long_term_memory is not None:
            res = self.long_term_memory.search(embeded_query, top_k)
            documents.extend(res)

        if self.knowledgebase is not None:
            res = self.knowledgebase.search(embeded_query, top_k)
            documents.extend(res)

        return documents
