# AzureServiceModule/AzureOpenAIClient.py
from openai import AzureOpenAI

# Azure OpenAI 클라이언트를 생성하여 반환합니다.
def get_azure_openai_client(api_key: str, endpoint: str) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint=endpoint
    )
