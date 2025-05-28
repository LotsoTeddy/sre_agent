import os
import uuid
from typing import Any, Literal, Optional

from opensearchpy import OpenSearch, Urllib3AWSV4SignerAuth, Urllib3HttpConnection, helpers
from pydantic import BaseModel
from src.retrieval.document import Document
from src.retrieval.vdb.vector import KnowledgeBaseVector, register_vector, VectorType
# from dotenv import load_dotenv
# load_dotenv()

class OpenSearchConfig(BaseModel):
    host: str = os.getenv("OPENSEARCH_HOST")
    port: int = os.getenv('OPENSEARCH_PORT') if os.getenv('OPENSEARCH_PORT') is not None else 9200
    secure: bool = True  # use_ssl
    verify_certs: bool = False
    auth_method: Literal["basic", "aws_managed_iam"] = "basic"
    user: Optional[str] = os.getenv("OPENSEARCH_USER")
    password: Optional[str] = os.getenv("OPENSEARCH_PASSWORD")

    @classmethod
    def validate_config(cls, values: dict) -> dict:
        if not values.get("host"):
            raise ValueError("config OPENSEARCH_HOST is required")
        if not values.get("port"):
            raise ValueError("config OPENSEARCH_PORT is required")
        if values.get("auth_method") == "aws_managed_iam":
            if not values.get("aws_region"):
                raise ValueError("config OPENSEARCH_AWS_REGION is required for AWS_MANAGED_IAM auth method")
            if not values.get("aws_service"):
                raise ValueError("config OPENSEARCH_AWS_SERVICE is required for AWS_MANAGED_IAM auth method")
        if not values.get("OPENSEARCH_SECURE") and values.get("OPENSEARCH_VERIFY_CERTS"):
            raise ValueError("verify_certs=True requires secure (HTTPS) connection")
        return values

    def create_aws_managed_iam_auth(self) -> Urllib3AWSV4SignerAuth:
        import boto3  # type: ignore

        return Urllib3AWSV4SignerAuth(
            credentials=boto3.Session().get_credentials(),
            region=self.aws_region,
            service=self.aws_service,  # type: ignore[arg-type]
        )

    def to_opensearch_params(self) -> dict[str, Any]:
        params = {
            "hosts": [{"host": self.host, "port": self.port}],
            "use_ssl": self.secure,
            "verify_certs": self.verify_certs,
            "connection_class": Urllib3HttpConnection,
            "pool_maxsize": 20,
        }
        ca_cert_path = os.getenv("OPENSEARCH_CA_CERT")
        if self.verify_certs and ca_cert_path:
            params["ca_certs"] = ca_cert_path

        if self.auth_method == "basic":
            print("Using basic authentication for OpenSearch Vector DB")

            params["http_auth"] = (self.user, self.password)
        elif self.auth_method == "aws_managed_iam":
            print("Using AWS managed IAM role for OpenSearch Vector DB")
            params["http_auth"] = self.create_aws_managed_iam_auth()

        return params


@register_vector
class OpenSearchVector(KnowledgeBaseVector):
    name: str = VectorType.OPENSEARCH.value

    def __init__(self, collection_name: str):
        super().__init__(collection_name)
        self._client_config = OpenSearchConfig()
        self._client = self._init_client(self._client_config)
        self._info = self._client.info()
        # print(self._info)

    def _init_client(self, config: OpenSearchConfig) -> OpenSearch:
        return OpenSearch(**config.to_opensearch_params())

    def _default_settings(self) -> dict:
        settings = {
            "index": {
                "knn": True
            }
        }
        return settings

    def _default_mappings(self, dim: int = 2048) -> dict:
        mappings = {
            "properties": {
                "page_content": {
                    "type": "text",
                },
                "vector": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "faiss",
                        "parameters": {"ef_construction": 64, "m": 8},
                    },
                },
                # "meatadata": {
                #     "type": "object",
                #     "properties": {
                #         "doc_id": {"type": "keyword"},
                #         "source": {"type": "keyword"},
                #     }
                # }
            }
        }
        return mappings

    def create_collection(
            self,
            embedding_dim: int,
    ):
        # todo: 添加互斥锁，防止出现index名的冲突
        if not self._client.indices.exists(index=self._collection_name):
            self._client.indices.create(
                index=self._collection_name,
                body={
                    'mappings': self._default_mappings(dim=embedding_dim),
                    'settings': self._default_settings()
                }
            )

        return

    def add_texts(self, documents: list[Document], **kwargs):
        actions = []
        for i in range(len(documents)):
            action = {
                "_op_type": "index",
                "_index": self._collection_name,
                "_source": {
                    "page_content": documents[i].page_content,
                    "vector": documents[i].vector,
                },
            }
            if self._client_config.aws_service not in ["aoss"]:
                action["_id"] = uuid.uuid4().hex
            actions.append(action)
            pass

        helpers.bulk(
            client=self._client,
            actions=actions,
            timeout=30,
            max_retries=3,
        )
        return

    def create(self, texts: list[Document], **kwargs):
        if texts[0].vector is not None:
            dim = len(texts[0].vector)
        else:
            dim = kwargs.get('dim', 2048)

        self.create_collection(embedding_dim=dim)
        self.add_texts(texts, **kwargs)
        return

    def delete(self) -> None:
        raise NotImplementedError

    def collection_exist(self) -> bool:
        try:
            return self._client.indices.exists(index=self._collection_name)
        except Exception as e:
            print(f"BadRequestError: {e}")
            if hasattr(e, 'body') and e.body:
                print(f"Error details: {e.body}")
            return False

    def search_by_vector(self, query_vector: list[float], **kwargs: Any) -> list[str]:
        top_k = kwargs.get('top_k', 5)
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_vector,
                        "k": top_k
                    }
                }
            },
        }

        response = self._client.search(index=self._collection_name, body=query)

        result_list = []
        for hit in response['hits']['hits']:
            result_list.append(hit['_source']['page_content'])

        return result_list

    def get_health(self):
        response = self._client.cat.health()
        print(response)


if __name__ == "__main__":
    # python -m src.retrieval.vdb.opensearch.opensearch_vector
    vector = OpenSearchVector(collection_name="test")