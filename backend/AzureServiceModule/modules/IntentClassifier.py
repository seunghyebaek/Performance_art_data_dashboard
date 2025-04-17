# AzureServiceModule/modules/IntentClassifier.py

class IntentClassifier:
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    # 사용자의 발화를 보고 intent 분류 (수집 / 검색 / 분석 중 하나)
    def classify_intent(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": """
            다음 사용자의 발화가 어떤 목적에 해당하는지 분류하세요.

            - "수집" → 사용자가 공연 기획 관련 정보를 제공하고 있어, 추가 질문을 통해 변수를 수집해야 함
            - "검색" → 사용자가 무언가를 알려달라고 요청하고 있어, 문서 검색이 필요함
            - "분석" → 사용자가 정보 분석, 예측, 통계 등을 요청하고 있어, 데이터 분석이 필요함

            다음 키워드가 있으면 "분석" 의도로 판단하세요: 분석, 예측, 계산, ROI, BEP, 통계, 현황, 추이, 총결산, 비교, 장르별, 지역별, 규모별

            아래 중 하나만 출력하세요: 수집 / 검색 / 분석
            """},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0,
            max_tokens=10
        )

        return response.choices[0].message.content.strip()
