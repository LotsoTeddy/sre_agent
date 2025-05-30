from google.adk.memory import VertexAiRagMemoryService, InMemoryMemoryService, BaseMemoryService
from google.adk.memory.base_memory_service import SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.sessions import Session
from google.adk.events import Event
from google.genai import types
from src.retrieval.vdb import generate_vector, ChromaVector, OpenSearchVector, VectorType
from src.retrieval.document import Document
from src.retrieval.embedding import ArkEmbeddings
from src.utils.times import get_current_time, get_yesterday_time
from src.utils.logger import get_logger
logger = get_logger(__name__)


def _user_key(app_name: str, user_id: str):
  return f'{app_name}-{user_id}'

def check_value(vector_type: str):
    # 遍历枚举类的所有 value
    valid_values = [item.value for item in VectorType]
    if vector_type not in valid_values:
        raise ValueError(f"{vector_type} must in VectorType")

# 负责记录历史操作
class VdbMemory(BaseMemoryService):
    def __init__(self, vector_type: str):
        super().__init__()
        check_value(vector_type)
        self._vector_type = vector_type
        self.embedding = ArkEmbeddings()



    async def add_session_to_memory(self, session: Session):
        user_key = _user_key(session.app_name, session.user_id)
        vector = generate_vector(
            name=self._vector_type, collection_name=user_key
        )
        text_list = []
        for event in session.events:
            if (event.content and event.content.parts
                    and event.content.parts[0].text is not None
                    and len(event.content.parts[0].text.strip()) > 0):
                text_list.append(
                    f"""{{"role": "{event.content.role}", "content":"{event.content.parts[0].text.strip()}" }}"""
                )
        # 因为会在第0次会话中触发，故设置为昨天，用以模拟长期记忆
        text = f"历史会话：\n会话发生时间：\n{get_yesterday_time()}"+"\n".join(text_list)

        vector.create(
            texts=[
                Document(
                    page_content=text,
                    vector=self.embedding.embed_query(text)
                )
            ]
        )

        pass


    async def search_memory(self, *, app_name: str, user_id: str, query: str) -> SearchMemoryResponse:
        user_key = _user_key(app_name, user_id)
        vector = generate_vector(
            name=self._vector_type, collection_name=user_key
        )
        if not vector.collection_exist():
            return SearchMemoryResponse()

        chunks = vector.search_by_vector(
            query_vector=self.embedding.embed_query(query)
        )
        if len(chunks) == 0:
            return SearchMemoryResponse()

        response = SearchMemoryResponse()
        history = "这是通过知识库工具查询到的历史信息："+"\n".join(chunks)

        # logger.debug(f"VdbMemory查询到的信息如下\n{history}")
        response.memories.append(
            MemoryEntry(
                content=types.Content(
                            role="model", parts=[
                                types.Part(text=history)
                            ]
                        ),
                author='memory_agent',
            )
        )

        return response