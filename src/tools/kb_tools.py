from google.adk.tools import FunctionTool

from src.retrieval.document import Document
from src.retrieval.vdb import generate_vector, OpenSearchVector, ChromaVector, VectorType
from src.retrieval.embedding import ArkEmbeddings
from src.utils.logger import get_logger
logger = get_logger(__name__)

def search_risk_operation(query: str) -> list[str]:
    """
    Call this function to return dangerous operations similar to or related to the query,
    and return them in the form of list[str]. This method is used to assist in determining whether a command is a high-risk operation.
    """

    vector = generate_vector(
        name=VectorType.CHROMA.value,
        collection_name="high_risk_opter"
    )
    embedding = ArkEmbeddings()

    res = vector.search_by_vector(
        query_vector=embedding.embed_query(query),
        top_k=10
    )
    logger.info(f"\n调用search_risk_operation函数，执行数据库搜索；搜索到的内容如下:\n{'\n'.join(res)}")
    return res


def prepare_data(data_path: str):

    vector = generate_vector(
        name=VectorType.CHROMA.value,
        collection_name="high_risk_opter"
    )
    if vector.collection_exist():
        return

    embed_client = ArkEmbeddings()
    # 读取txt文件，按行保存为list
    with open(data_path, 'r', encoding='utf-8') as f:
        data = f.readlines()
    # 去除换行符
    data = [x.strip() for x in data]
    # 生成向量
    embeddings = embed_client.embed_documents(data)
    vector.create(
        texts=[
            Document(
                page_content=data[i],
                vector=embeddings[i]
            )
            for i in range(len(data))
        ]
    )

# if __name__ == '__main__':
    # prepare_data('examples/risky_comands.txt')
    # x = search_risk_operation("rm -rf")
    #
    # print(x)
