from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3


class OpenSearchService:
    def __init__(self, host, region="ap-south-1"):
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            "es",
            session_token=credentials.token,
        )

        self.client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )

    def create_index(self, index_name):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name)
            return f"Index '{index_name}' created"
        return f"Index '{index_name}' already exists"

    def index_document(self, index_name, doc_id, body):
        return self.client.index(index=index_name, id=doc_id, body=body)

    def search(self, index_name, query):
        return self.client.search(
            index=index_name,
            body={
                "query": {
                    "match": query
                }
            }
        )