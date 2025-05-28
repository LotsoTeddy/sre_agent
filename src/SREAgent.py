import asyncio

from arkitect.core.component.tool.mcp_client import MCPClient
from src.knowledgebase import KnowledgeBase
from src.memory import LongTermMemory, Session, ShortTermMemory
from volcenginesdkarkruntime import Ark


class SREAgent:
    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        model,
        knowledgebase: KnowledgeBase = None,
        short_term_memory: ShortTermMemory = None,
        long_term_memory: LongTermMemory = None,
    ):
        self.name = name
        self.description = description
        self.instruction = instruction

        self.model = model

        self.knowledgebase = knowledgebase

        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory

        self.session = Session()
        self.session.add(
            message={
                "role": "system",
                "content": self.instruction,
            }
        )

    async def run(self, prompt: str):
        documents = self.search(prompt)
        if documents != []:
            prompt = f"{prompt} \n The references are: {documents}"

        message = {"role": "user", "content": prompt}
        self.session.add(message=message)

        response = await self.model.completions.create(
            messages=self.session.get(), stream=False
        )
        self.session.add(response.choices[0].message.dict())

        return response.choices[0].message.content

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """We obey the following RAG flow:
        1. Search long-term memory
        2. Search short-term memory
        3. Search knowledgebase
        """
        if any(
            [
                self.short_term_memory is None,
                self.long_term_memory is None,
                self.knowledgebase is None,
            ]
        ):
            return []

        embeded_query = []
        embedding_client = Ark()
        response = embedding_client.embeddings.create(
            model="doubao-embedding-text-240715", input=[embeded_query]
        )
        embeded_query = [response.data[i].embedding for i in range(len(response.data))]

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
