# AzureServiceModule/modules/AISearchClient.py
from ..util.CleanText import cleanText

class AISearchService:
    def __init__(self, client, deployment, search_key, search_endpoint, search_index):
        self.client = client
        self.deployment = deployment
        self.search_key = search_key
        self.search_endpoint = search_endpoint
        self.search_index = search_index

    def query(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": "너는 문화예술행사 전문 에이전트야. 한국어로 대답하고, 프롬프트를 잘 해석해서 대답해줘. 문서 참조도 충실하게 해줘."},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": self.search_endpoint,
                            "index_name": self.search_index,
                            "semantic_configuration": f"{self.search_index}-semantic-configuration",
                            "query_type": "semantic",
                            "in_scope": True,
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 5,
                            "authentication": {
                                "type": "api_key",
                                "key": self.search_key
                            }
                        }
                    }
                ]
            }
        )
        res = cleanText(response.choices[0].message.content.strip())
        return res
