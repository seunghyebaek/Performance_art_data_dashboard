numeric_keys = [
    "capacity", "star_power", "ticket_price", "marketing_budget", "sns_mention_count",
    "daily_sales", "booking_rate", "ad_exposure", "sns_mention_daily",
    "production_cost", "variable_cost_rate", "accumulated_sales", "duration"
]
date_keys = ["start_date"]

categorical_keys = {
    "genre": ["대중무용", "대중음악", "무용", "뮤지컬", "복합", "서양음악", "서커스/마술", "연극", "한국음악"],
    "region": ["강원특별자치도", "경기도", "경상남도", "경상북도", "광주광역시", "대구광역시", "대전광역시",
               "부산광역시", "서울특별시", "세종특별자치시", "울산광역시", "인천광역시",
               "전라남도", "전라북도", "제주특별자치도", "충청남도", "충청북도"],
    "promo_event_flag": ["True", "False"]
}

# 모든 수집 대상 변수명들의 리스트(숫자형 + 날짜형 + 범주형) 
required_keys = numeric_keys + date_keys + list(categorical_keys.keys())

# 기획 단계키
planning_stage_keys = [
    "genre", "region", "start_date", "capacity", "star_power",
    "ticket_price", "marketing_budget", "sns_mention_count",
    "production_cost", "variable_cost_rate", "duration"
]
# 판매 단계키 
sales_stage_keys = [
    "genre", "region", "start_date", "capacity", "star_power",
    "ticket_price", "marketing_budget", "sns_mention_count",
    "daily_sales", "booking_rate", "ad_exposure", "production_cost",
    "variable_cost_rate", "accumulated_sales", "sns_mention_daily", "promo_event_flag", "duration"
]