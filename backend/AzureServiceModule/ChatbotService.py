# backend/AzureServiceModule/ChatbotService.py

from .modules.AzureOpenAIClient import get_azure_openai_client
from .modules.IntentClassifier import IntentClassifier
from .modules.StageDetector import StageDetector
from .modules.VariableExtractor import AITextExtractor
from .modules.PromptGenerator import PromptGenerator
from .modules.AISearchClient import AISearchService
from .config.VariableConfig import required_keys, categorical_keys, planning_stage_keys, sales_stage_keys
import json
import re
import httpx  # 비동기 HTTP 요청을 위한 라이브러리
from datetime import datetime

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("chatbot")

class ChatbotService:
    def __init__(self, api_key, endpoint, deployment, search_key, search_endpoint, search_index):
        # Azure OpenAI 클라이언트 초기화
        self.client = get_azure_openai_client(api_key, endpoint)
        self.deployment = deployment
        
        # 4가지 핵심 기능 초기화
        self.extractor = AITextExtractor(self.client, self.deployment, required_keys, categorical_keys)  # JSON 변수 추출기
        self.prompter = PromptGenerator(self.client, self.deployment, categorical_keys)                  # 챗봇 질문 생성기
        self.search = AISearchService(self.client, self.deployment, search_key, search_endpoint, search_index)  # 문서 검색기
        self.detector = StageDetector(self.client, self.deployment)
        self.classifier = IntentClassifier(self.client, self.deployment)

        # 상태 정보
        self.collected_vars = {}
        self.summary = None
        self.last_asked_key = None
        
        # ML API 기본 URL (같은 서버에서 실행 중이라고 가정)
        self.ml_api_base_url = "http://localhost:8000/api/ml"  # 필요에 따라 조정
        
    # 날짜를 숫자로 변환하는 함수 (ML 모델 입력용)
    def _convert_date_to_numeric(self, date_str):
        """YYYY-MM-DD 형식의 날짜를 1~365 사이의 숫자로 변환"""
        if not date_str:
            return 1.0  # 기본값
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_of_year = date_obj.timetuple().tm_yday  # 1부터 365(366)까지의 날짜
            return float(day_of_year)
        except:
            return 1.0  # 변환 실패 시 기본값

    # 필요한 분석 유형 결정 함수
    def _determine_analysis_type(self, user_input, stage):
        """사용자 입력과 단계를 기반으로 필요한 분석 유형 결정"""
        # 통계 분석 우선 검출 (단계 구분 없음)
        if re.search(r"(장르별|장르.{0,5}통계|장르.{0,5}분석|장르.{0,5}결산|장르.{0,5}추이)", user_input, re.IGNORECASE):
            return ["genre_stats"]
            
        if re.search(r"(지역별|지역.{0,5}통계|지역.{0,5}분석|지역.{0,5}결산|지역.{0,5}추이)", user_input, re.IGNORECASE):
            return ["regional_stats"]
        
        if re.search(r"(공연장.{0,5}규모|규모별|좌석.{0,5}규모|규모.{0,5}분석)", user_input, re.IGNORECASE):
            return ["venue_scale_stats"]
        
        # 티켓 위험도 분석은 단계와 관계없이 요청 가능하도록 설정
        if re.search(r"(티켓.{0,5}위험|위험.{0,5}분석|티켓.{0,5}리스크|위험도|위험|리스크|가능성|실패)", user_input, re.IGNORECASE):
            return ["ticket_risk_selling"]
        
        # 기존 분석 유형 (단계 구분 적용)
        # 기본 분석 유형
        if stage == "기획":
            analysis_types = ["accumulated_sales_planning", "roi_bep_planning"]
        else:  # 판매 단계
            analysis_types = ["accumulated_sales_selling", "roi_bep_selling", "ticket_risk_selling"]
        
        # 특정 분석 유형 검출
        if re.search(r"(관객|티켓|판매량|매출액)", user_input, re.IGNORECASE):
            if stage == "기획":
                return ["accumulated_sales_planning"]
            else:
                return ["accumulated_sales_selling"]
                
        elif re.search(r"(손익|수익|ROI|BEP|손익분기점)", user_input, re.IGNORECASE):
            if stage == "기획":
                return ["roi_bep_planning"]
            else:
                return ["roi_bep_selling"]
                
        # 명확한 패턴이 없으면 단계별 기본 분석 실행
        return analysis_types
    
    # 변수 포맷 변환 함수
    def _format_variables_for_ml_api(self, analysis_type):
        """수집된 변수를 ML API 형식에 맞게 변환"""
        formatted_vars = self.collected_vars.copy()
        
        # 날짜를 숫자로 변환
        if "start_date" in formatted_vars:
            formatted_vars["start_date_numeric"] = self._convert_date_to_numeric(formatted_vars["start_date"])
        
        # 모든 숫자 필드를 float로 변환
        numeric_fields = [
            "capacity", "star_power", "ticket_price", "marketing_budget", 
            "sns_mention_count", "daily_sales", "booking_rate", "ad_exposure", 
            "sns_mention_daily", "production_cost", "variable_cost_rate", 
            "accumulated_sales", "duration"
        ]
        
        for field in numeric_fields:
            if field in formatted_vars:
                try:
                    if isinstance(formatted_vars[field], str):
                        # 문자열에서 숫자만 추출
                        formatted_vars[field] = float(''.join(c for c in formatted_vars[field] if c.isdigit() or c == '.'))
                    else:
                        formatted_vars[field] = float(formatted_vars[field])
                except (ValueError, TypeError):
                    # 변환 실패 시 해당 필드 제거
                    formatted_vars.pop(field, None)
        
        # promo_event_flag를 정수로 변환
        if "promo_event_flag" in formatted_vars:
            if isinstance(formatted_vars["promo_event_flag"], str):
                formatted_vars["promo_event_flag"] = 1 if formatted_vars["promo_event_flag"].lower() == "true" else 0
            elif isinstance(formatted_vars["promo_event_flag"], bool):
                formatted_vars["promo_event_flag"] = 1 if formatted_vars["promo_event_flag"] else 0
        
        # 분석 유형별 필수 필드 설정
        if analysis_type == "accumulated_sales_planning":
            defaults = {
                "genre": formatted_vars.get("genre", "뮤지컬"),
                "region": formatted_vars.get("region", "서울특별시"),
                "start_date_numeric": formatted_vars.get("start_date_numeric", 1.0),
                "capacity": formatted_vars.get("capacity", 502000.5),
                "star_power": formatted_vars.get("star_power", 280.0),
                "ticket_price": formatted_vars.get("ticket_price", 40439.5),
                "marketing_budget": formatted_vars.get("marketing_budget", 8098512.5),
                "sns_mention_count": formatted_vars.get("sns_mention_count", 38.0),
                "duration": formatted_vars.get("duration", 1)
            }
            return defaults
        
        elif analysis_type == "accumulated_sales_selling":
            defaults = {
                "genre": formatted_vars.get("genre", "뮤지컬"),
                "region": formatted_vars.get("region", "서울특별시"),
                "start_date_numeric": formatted_vars.get("start_date_numeric", 1.0),
                "capacity": formatted_vars.get("capacity", 502000.5),
                "star_power": formatted_vars.get("star_power", 280.0),
                "ticket_price": formatted_vars.get("ticket_price", 40439.5),
                "marketing_budget": formatted_vars.get("marketing_budget", 8098512.5),
                "sns_mention_count": formatted_vars.get("sns_mention_count", 38.0),
                "daily_sales": formatted_vars.get("daily_sales", 2.0),
                "booking_rate": formatted_vars.get("booking_rate", 0.7),
                "ad_exposure": formatted_vars.get("ad_exposure", 303284.5),
                "sns_mention_daily": formatted_vars.get("sns_mention_daily", 38.0),
                "duration": formatted_vars.get("duration", 1)
            }
            return defaults
        
        elif analysis_type == "roi_bep_planning" or analysis_type == "roi_bep_selling":
            defaults = {
                "production_cost": formatted_vars.get("production_cost", 570111934.0),
                "marketing_budget": formatted_vars.get("marketing_budget", 8098512.5),
                "ticket_price": formatted_vars.get("ticket_price", 40349.5),
                "capacity": formatted_vars.get("capacity", 280.0),
                "variable_cost_rate": formatted_vars.get("variable_cost_rate", 0.17755),
                "accumulated_sales": formatted_vars.get("accumulated_sales", 105.0),
                "duration": formatted_vars.get("duration", 1)
            }
            return defaults
        
        elif analysis_type == "ticket_risk_selling":
            defaults = {
                "genre": formatted_vars.get("genre", "뮤지컬"),
                "region": formatted_vars.get("region", "서울특별시"),
                "start_date_numeric": formatted_vars.get("start_date_numeric", 1.0),
                "capacity": formatted_vars.get("capacity", 280.0),
                "star_power": formatted_vars.get("star_power", 1.0),
                "daily_sales": formatted_vars.get("daily_sales", 2.0),
                "accumulated_sales": formatted_vars.get("accumulated_sales", 105.0),
                "ad_exposure": formatted_vars.get("ad_exposure", 303284.5),
                "sns_mention_daily": formatted_vars.get("sns_mention_daily", 0.0),
                "promo_event_flag": formatted_vars.get("promo_event_flag", 0),
                "duration": formatted_vars.get("duration", 1)
            }
            return defaults
        
        return formatted_vars
        
    # 호출 실패 시 가상 응답 제공 함수
    def _get_fallback_response(self, analysis_type):
        """API 호출 실패 시 가상 응답 생성"""
        logger.info(f"{analysis_type}에 대한 가상 응답 생성")
        
        if analysis_type == "accumulated_sales_planning":
            return {"predictions": [15000]}
        elif analysis_type == "roi_bep_planning":
            return {"predictions": [15.5, 8000]}
        elif analysis_type == "accumulated_sales_selling":
            return {"predictions": [20000]}
        elif analysis_type == "roi_bep_selling":
            return {"predictions": [18.5, 9500]}
        elif analysis_type == "ticket_risk_selling":
            return {"risk_labels": [0]}
        elif analysis_type == "genre_stats":
            return {
                "genre_stats": {
                    "genre": ["뮤지컬", "연극", "서양음악(클래식)", "대중음악", "무용(서양/한국)", "한국음악(국악)", "서커스/마술", "복합"],
                    "performance_count": [3006, 2932, 8199, 3970, 840, 1356, 835, 440],
                    "audience": [7831448, 2836558, 3290415, 6302709, 606737, 436947, 692155, 225613],
                    "ticket_revenue": [465122497, 73411508, 100996136, 756977444, 20633422, 4869454, 28565775, 2799943]
                }
            }
        elif analysis_type == "regional_stats":
            return {
                "regional_stats": {
                    "region": ["서울", "경기", "부산", "대구", "인천"],
                    "performance_count": [9966, 2917, 1311, 1279, 687],
                    "show_count": [82160, 10807, 5429, 5146, 2231],
                    "total_ticket_sales": [13384094, 2549324, 1062750, 1002533, 823153],
                    "total_ticket_revenue": [946566611, 127171128, 82282070, 56503689, 76098489]
                }
            }
        elif analysis_type == "venue_scale_stats":
            return {
                "venue_scale_stats": {
                    "year": [2024, 2024, 2024, 2024, 2024, 2024, 2024],
                    "scale": ["10,000석 이상", "5,000~10,000석 미만", "1,000~5,000석 미만", "500~1,000석 미만", "300~500석 미만", "1~300석 미만", "0석(좌석미상)"],
                    "performance_count": [132, 131, 4038, 4558, 4135, 7147, 1493],
                    "total_ticket_sales": [2682816, 734900, 8227156, 3504875, 2762187, 3429763, 898841]
                }
            }
        
        return {"error": "알 수 없는 분석 유형"}

    
    # ML 직접 호출 (api/chatbot/response 로 결과 데이터 반환)
    async def _call_ml_api(self, analysis_type, formatted_vars):
        """ML API 내부 직접 호출"""
        try:
            # ML 모듈에서 함수 직접 임포트
            from backend.ModelPredictionModule.analysis_module import (
                predict_acc_sales_planning,
                predict_acc_sales_selling,
                predict_roi_bep_planning,
                predict_roi_bep_selling,
                predict_ticket_risk,
                get_genre_stats,
                get_regional_stats,
                get_venue_scale_stats
            )
            
            # 통계 분석 (입력 데이터 없이 호출)
            if analysis_type == "genre_stats":
                stats = get_genre_stats()
                return stats
            
            elif analysis_type == "regional_stats":
                stats = get_regional_stats()
                return stats
                
            elif analysis_type == "venue_scale_stats":
                stats = get_venue_scale_stats()
                return stats
            
            # 기존 예측 분석 (입력 데이터 필요)
            # 단일 객체를 리스트로 포장
            input_data = [formatted_vars]
            
            # 직접 함수 호출
            if analysis_type == "accumulated_sales_planning":
                preds = predict_acc_sales_planning(input_data)
                return {"predictions": preds}
            elif analysis_type == "roi_bep_planning":
                preds = predict_roi_bep_planning(input_data)
                return {"predictions": preds}
            elif analysis_type == "accumulated_sales_selling":
                preds = predict_acc_sales_selling(input_data)
                return {"predictions": preds}
            elif analysis_type == "roi_bep_selling":
                preds = predict_roi_bep_selling(input_data)
                return {"predictions": preds}
            elif analysis_type == "ticket_risk_selling":
                preds = predict_ticket_risk(input_data)
                return {"risk_labels": preds}
            else:
                return self._get_fallback_response(analysis_type)
        except Exception as e:
            logger.error(f"직접 함수 호출 오류: {str(e)}")
            return self._get_fallback_response(analysis_type)
    
    # 분석 결과 해석 함수
    def _interpret_analysis_results(self, analysis_type, results):
        """분석 결과를 사용자 친화적인 텍스트로 변환"""
        try:
            logger.debug(f"분석 유형: {analysis_type}, 결과 구조: {type(results)}")
            logger.debug(f"결과 내용: {results}")
            
            if "error" in results:
                return f"분석 중 오류가 발생했습니다: {results['error']}"
            
            # 티켓 리스크 분석 (analysis_type 또는 risk_labels로 판단)
            if analysis_type == "ticket_risk_selling" or "risk_labels" in results:
                if "risk_labels" in results:
                    risk_labels = results["risk_labels"]
                    # 리스트가 아니면 리스트로 변환
                    if not isinstance(risk_labels, list):
                        risk_labels = [risk_labels]
                    # 빈 리스트면 기본값 설정
                    if not risk_labels:
                        risk_labels = [0]
                        
                    try:
                        risk_label = int(float(risk_labels[0]))
                    except (ValueError, TypeError, IndexError):
                        risk_label = 0
                    
                    # 0, 1, 2 값에 따른 리스크 레벨 설정
                    risk_levels = {
                        0: "낮음",
                        1: "중간",
                        2: "높음"
                    }
                    risk_level = risk_levels.get(risk_label, "알 수 없음")
                    
                    risk_text = f"⚠️ 티켓 판매 위험도: {risk_level}\n"
                    
                    # 리스크 레벨별 조언
                    if risk_label == 0:
                        advice = "현재 판매 추세가 양호합니다. 현재 전략을 유지하세요."
                    elif risk_label == 1:
                        advice = "판매 추세가 기대에 미치지 못합니다. 마케팅 활동 강화를 고려해보세요."
                    elif risk_label == 2:
                        advice = "판매 위험도가 높습니다. 추가 마케팅 활동과 프로모션을 적극 고려하세요."
                    else:
                        advice = "판매 추세를 분석할 충분한 데이터가 없습니다."
                    
                    return risk_text + advice
            
            # 통계 분석 결과 해석
            if analysis_type == "genre_stats":
                if "genre_stats" in results:
                    stats = results["genre_stats"]
                    genres = stats.get("genre", [])
                    counts = stats.get("performance_count", [])
                    audiences = stats.get("audience", [])
                    revenues = stats.get("ticket_revenue", [])
                    
                    # 상위 3개 장르 추출
                    if len(genres) > 0:
                        # 공연 작수 기준 상위 3개
                        top_genres_idx = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)[:3]
                        top_genres = [genres[i] for i in top_genres_idx]
                        top_counts = [counts[i] for i in top_genres_idx]
                        
                        response = f"🎭 장르별 통계 분석 결과:\n\n"
                        response += f"공연 작품 수가 가장 많은 장르는 '{top_genres[0]}'로 {top_counts[0]}개 작품이 공연되었습니다.\n"
                        response += f"그 다음으로 '{top_genres[1]}'({top_counts[1]}개), '{top_genres[2]}'({top_counts[2]}개) 순입니다.\n\n"
                        
                        # 총 공연 작품 수와 관객 수
                        total_performances = sum(counts)
                        total_audience = sum(audiences)
                        total_revenue = sum(revenues)
                        
                        response += f"전체 {len(genres)}개 장르에서 총 {total_performances}개 작품이 공연되었으며, "
                        response += f"총 관객 수는 {total_audience:,}명, 티켓 매출액은 {total_revenue:,}원입니다.\n"
                        
                        return response
                        
                return "장르별 통계 데이터가 준비되었습니다."
                
            elif analysis_type == "regional_stats":
                if "regional_stats" in results:
                    stats = results["regional_stats"]
                    regions = stats.get("region", [])
                    counts = stats.get("performance_count", [])
                    shows = stats.get("show_count", [])
                    sales = stats.get("total_ticket_sales", [])
                    
                    if len(regions) > 0:
                        response = f"📍 지역별 통계 분석 결과:\n\n"
                        response += f"공연이 가장 많이 열린 지역은 '{regions[0]}'로 {counts[0]}개 공연, {shows[0]}회 상연이 진행되었습니다.\n"
                        
                        # 상위 3개 지역 비교
                        if len(regions) >= 3:
                            response += f"그 다음으로 '{regions[1]}'({counts[1]}개), '{regions[2]}'({counts[2]}개) 순입니다.\n\n"
                        
                        # 티켓 판매 비교
                        if len(sales) > 0:
                            top_sales_idx = sorted(range(len(sales)), key=lambda i: sales[i], reverse=True)[0]
                            response += f"티켓 판매가 가장 많은 지역은 '{regions[top_sales_idx]}'로 총 {sales[top_sales_idx]:,}장이 판매되었습니다.\n"
                        
                        return response
                        
                return "지역별 통계 데이터가 준비되었습니다."
                
            elif analysis_type == "venue_scale_stats":
                if "venue_scale_stats" in results:
                    stats = results["venue_scale_stats"]
                    years = stats.get("year", [])
                    scales = stats.get("scale", [])
                    counts = stats.get("performance_count", [])
                    sales = stats.get("total_ticket_sales", [])
                    
                    if len(years) > 0 and len(scales) > 0:
                        # 최신 연도 데이터 추출
                        latest_year = max(years) if years else 0
                        latest_year_indices = [i for i, y in enumerate(years) if y == latest_year]
                        
                        latest_scales = [scales[i] for i in latest_year_indices]
                        latest_counts = [counts[i] for i in latest_year_indices]
                        
                        # 가장 많은 공연이 열린
                        if latest_counts:
                            max_idx = latest_counts.index(max(latest_counts))
                            response = f"🏛️ 공연장 규모별 통계 분석 결과 ({latest_year}년):\n\n"
                            response += f"가장 많은 공연이 열린 공연장 규모는 '{latest_scales[max_idx]}'로 {latest_counts[max_idx]}개 공연이 진행되었습니다.\n"
                            
                            # 작년과 비교
                            prev_year = latest_year - 1
                            prev_year_indices = [i for i, y in enumerate(years) if y == prev_year]
                            
                            if prev_year_indices:
                                prev_scales = [scales[i] for i in prev_year_indices]
                                prev_counts = [counts[i] for i in prev_year_indices]
                                
                                # 같은 규모 찾기
                                if latest_scales[max_idx] in prev_scales:
                                    prev_idx = prev_scales.index(latest_scales[max_idx])
                                    change = latest_counts[max_idx] - prev_counts[prev_idx]
                                    change_text = f"증가했습니다" if change > 0 else f"감소했습니다" if change < 0 else "동일합니다"
                                    response += f"이는 {prev_year}년({prev_counts[prev_idx]}개)에 비해 {abs(change)}개 {change_text}.\n"
                            
                            return response
                        
                return "공연장 규모별 통계 데이터가 준비되었습니다."
            
            # 중첩된 predictions 구조 처리
            if "predictions" in results and isinstance(results["predictions"], dict):
                nested_results = results["predictions"]
                
                if analysis_type == "accumulated_sales_planning" or analysis_type == "accumulated_sales_selling":
                    # 중첩된 predictions 배열에서 첫 번째 값 추출
                    predictions_array = nested_results.get("predictions", [0])
                    value = predictions_array[0] if len(predictions_array) > 0 else 0
                    return f"🎭 예상 관객 수: 약 {int(value):,}명\n"
                    
                elif analysis_type == "roi_bep_planning" or analysis_type == "roi_bep_selling":
                    # 중첩된 predictions 배열의 배열에서 값 추출
                    predictions_array = nested_results.get("predictions", [[0, 0]])
                    value = predictions_array[0] if len(predictions_array) > 0 else [0, 0]
                    
                    roi = value[0] if len(value) > 0 else 0
                    bep = value[1] if len(value) > 1 else 0
                    
                    roi_percentage = roi * 100  # 비율을 퍼센트로 변환 (필요한 경우)
                    
                    roi_text = f"📈 예상 ROI(투자수익률): {roi_percentage:.2f}%\n"
                    bep_text = f"⚖️ 손익분기점(BEP): 약 {int(bep):,}명의 관객\n"
                    
                    return roi_text + bep_text
            
            # 기존 비중첩 구조 처리 (이전 구조와의 호환성 유지)
            elif "predictions" in results and isinstance(results["predictions"], list):
                if analysis_type == "accumulated_sales_planning" or analysis_type == "accumulated_sales_selling":
                    value = results.get("predictions", [0])[0]
                    return f"🎭 예상 관객 수: 약 {int(value):,}명\n"
                    
                elif analysis_type == "roi_bep_planning" or analysis_type == "roi_bep_selling":
                    value = results.get("predictions", [0, 0])
                    roi = value[0]
                    bep = value[1] if len(value) > 1 else 0
                    
                    roi_text = f"📈 예상 ROI(투자수익률): {roi:.2f}%\n"
                    bep_text = f"⚖️ 손익분기점(BEP): 약 {int(bep):,}명의 관객\n"
                    
                    return roi_text + bep_text
                    
            return "분석 결과를 해석할 수 없습니다."
            
        except Exception as e:
            logger.error(f"결과 해석 오류: {str(e)}", exc_info=True)
            return f"결과 해석 중 오류 발생: {str(e)}"
            
    
    # 기존 handle_user_input 함수 확장
    async def handle_user_input(self, user_input, history):
        if not isinstance(history, list):
            history = []

        # 1. 사용자 의도 분류: 수집 / 검색 / 분석
        intent = self.classifier.classify_intent(user_input)
        stage = self.detector.detect_stage(user_input)
        
        logger.debug(f"사용자 입력: '{user_input}'")
        logger.debug(f"감지된 의도: {intent}")
        logger.debug(f"감지된 단계: {stage}")
        
        reply_parts = []
        analysis_results = {}

        # 2-1. JSON 변수 수집
        if intent in ["수집"]:
            extracted = self.extractor.extract_variables(user_input, fallback_key=self.last_asked_key)
            logger.debug(f"추출된 변수: {extracted}")
            
            for key, val in extracted.items():
                if val is not None:
                    self.collected_vars[key] = val

        # 2-2. 분석 요청 처리 - 의도가 "분석" 또는 "혼합"일 때만 수행
        if intent in ["분석"]:
            analysis_types = self._determine_analysis_type(user_input, stage)
            logger.debug(f"결정된 분석 유형: {analysis_types}")
            
            # 분석 결과 모음
            analysis_results_text = []
            
            for analysis_type in analysis_types:
                formatted_vars = self._format_variables_for_ml_api(analysis_type)
                logger.debug(f"API 호출 전 변수: {formatted_vars}")
                
                api_result = await self._call_ml_api(analysis_type, formatted_vars)
                logger.debug(f"API 응답: {api_result}")
                
                result_text = self._interpret_analysis_results(analysis_type, api_result)
                logger.debug(f"해석된 결과: {result_text}")
                
                analysis_results_text.append(result_text)
                analysis_results[analysis_type] = api_result
            
            # 분석 결과 추가
            if analysis_results_text:
                analysis_text = "## 📊 분석 결과\n\n" + "\n".join(analysis_results_text)
                logger.debug(f"추가될 분석 결과: {analysis_text}")
                reply_parts.append(analysis_text)
            else:
                logger.warning("분석 결과가 비어있음")

        # 2-3. 추가 유도 질문 생성
        next_question, next_key = self.prompter.generate(self.collected_vars, user_input, stage)
        if next_key:
            self.last_asked_key = next_key
        reply_parts.append(next_question)

        # 3. AI 문서 검색
        if intent in ["검색"]:
            summary = self.search.query(user_input)
            # reply_parts.append("📖 관련 문서 요약:\n\n" + summary)

        # 4. 응답 및 상태 반환
        full_reply = "\n\n".join(reply_parts)
        history.append((user_input, full_reply))
        
        logger.debug(f"최종 응답 구성 요소: {reply_parts}")
        logger.debug(f"현재 수집된 변수: {self.collected_vars}")

        return {
            "chat_history": history,
            "response_text": full_reply,
            "structured_data": self.collected_vars,
            "related_docu" : self.summary,
            "analysis_results": analysis_results,
            "intent": intent,
            "stage": stage,
        }