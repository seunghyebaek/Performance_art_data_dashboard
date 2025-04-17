# AzureServiceModule/modules/StageDetector.py

class StageDetector:
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment
    # 사용자의 발화를 보고 기획 / 판매 단계 중 하나를 분류
    def detect_stage(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": """
            당신은 공연 기획 단계를 분류하는 전문가입니다. 사용자의 발화를 분석하여 다음 두 단계 중 하나로 정확히 분류하세요:

            1. "기획" - 다음 패턴 중 하나 이상 발견될 때:
            - 아직 공연이 시작되지 않은 상태에 대한 언급
            - "준비 중이에요", "기획 중입니다", "계획하고 있어요" 등의 표현
            - 예산 계획, 장소 선정, 출연진 캐스팅 등 사전 준비 관련 내용
            - 미래 시제로 공연에 대해 이야기함 ("할 예정이에요", "진행할 계획입니다")
            - "어떻게 하면 좋을까요?", "얼마로 책정해야 할까요?" 등 의사결정 관련 질문

            2. "판매" - 다음 패턴 중 하나 이상 발견될 때:
            - 이미 진행 중이거나 판매가 시작된 공연에 대한 언급
            - "티켓 판매율", "예매 현황", "관객 반응" 등 실행 단계 지표 언급
            - "프로모션을 진행 중입니다", "광고를 집행하고 있어요" 등 현재 마케팅 활동
            - 일일 판매량, 예매율, 광고 효과 등 판매/홍보 관련 구체적 수치 언급
            - "판매가 저조한데", "반응이 좋아요" 등 현재 상황에 대한 평가

            모호한 경우 판단 기준:
            - 시제가 미래형이면 "기획"
            - 시제가 현재형이고 실행/판매 관련 내용이면 "판매"
            - 예산, 장소 등 기본 계획에 관한 질문만 있으면 "기획"
            - 마케팅 효과, 관객 반응 등 피드백에 관한 내용이 있으면 "판매"

            정확히 한 단어만 출력하세요: 기획 / 판매
        
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
