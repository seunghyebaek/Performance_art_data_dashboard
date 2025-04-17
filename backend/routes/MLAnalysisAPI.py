from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import numpy as np

# 주의: 챗봇 대화를 통한 분석은 /api/chatbot/response 엔드포인트를 통해 반환됩니다.

# 아래 import 시 경로에 주의 (폴더 구조에 맞게 조정)
from ModelPredictionModule.analysis_module import (
    predict_acc_sales_planning,
    predict_acc_sales_selling,
    predict_roi_bep_planning,
    predict_roi_bep_selling,
    predict_ticket_risk,
    get_genre_stats,
    get_regional_stats,
    get_venue_scale_stats
)

router = APIRouter()

# ------------------------------------------
# 1) 회귀: 관객 수 예측 - 기획 단계
# ------------------------------------------
class AccSalesPlanningInput(BaseModel):
    genre: str
    region: str = "서울특별시"
    start_date_numeric: float = 1.0
    capacity: float = 502000.5
    star_power: float = 280.0
    ticket_price: float = 40439.5
    marketing_budget: float = 8098512.5
    sns_mention_count: float = 38.0
    
    class Config:
        extra = "ignore"  # 정의되지 않은 추가 필드는 무시합니다.

@router.post("/accumulated_sales_planning")
def api_predict_acc_sales_planning(inputs: List[AccSalesPlanningInput]):
    input_data = [inp.dict() for inp in inputs]
    preds = predict_acc_sales_planning(input_data)
    return {"predictions": np.array(preds).tolist()}

# ------------------------------------------
# 2) 회귀: 관객 수 예측 - 판매 단계
# ------------------------------------------
class AccSalesSellingInput(BaseModel):
    genre: str
    region: str = "서울특별시"
    start_date_numeric: float = 1.0
    capacity: float = 502000.5
    star_power: float = 280.0
    ticket_price: float = 40439.5
    marketing_budget: float = 8098512.5
    sns_mention_count: float = 38.0
    daily_sales: float = 2.0
    booking_rate: float = 0.7
    ad_exposure: float = 303284.5
    sns_mention_daily: float = 38.0

    class Config:
        extra = "ignore"


@router.post("/accumulated_sales_selling")
def api_predict_acc_sales_selling(inputs: List[AccSalesSellingInput]):
    input_data = [inp.dict() for inp in inputs]
    preds = predict_acc_sales_selling(input_data)
    return {"predictions": np.array(preds).tolist()}


# ------------------------------------------
# 3) 회귀: 손익 예측(ROI, BEP) - 기획 단계
# ------------------------------------------
class ROI_BEP_PlanningInput(BaseModel):
    production_cost: float = 570111934.0
    marketing_budget: float = 8098512.5
    ticket_price: float = 40349.5
    capacity: float = 280.0
    variable_cost_rate: float = 0.17755
    accumulated_sales: float = 105.0

    class Config:
        extra = "ignore"


@router.post("/roi_bep_planning")
def api_predict_roi_bep_planning(inputs: List[ROI_BEP_PlanningInput]):
    input_data = [inp.dict() for inp in inputs]
    preds = predict_roi_bep_planning(input_data)
    return {"predictions": np.array(preds).tolist()}


# ------------------------------------------
# 4) 회귀: 손익 예측(ROI, BEP) - 판매 단계
# ------------------------------------------
class ROI_BEP_SellingInput(BaseModel):
    production_cost: float = 570111934.0
    marketing_budget: float = 8098512.5
    ticket_price: float = 40349.5
    capacity: float = 280.0
    variable_cost_rate: float = 0.17755
    accumulated_sales: float = 105.0

    class Config:
        extra = "ignore"


@router.post("/roi_bep_selling")
def api_predict_roi_bep_selling(inputs: List[ROI_BEP_SellingInput]):
    input_data = [inp.dict() for inp in inputs]
    preds = predict_roi_bep_selling(input_data)
    return {"predictions": np.array(preds).tolist()}


# ------------------------------------------
# 5) 분류: 티켓 판매 위험 예측 - 판매 단계 (조기 경보)
# ------------------------------------------
class TicketRiskInput(BaseModel):
    genre: str
    region: str = "서울특별시"
    start_date_numeric: float = 1.0
    capacity: float = 280.0
    star_power: float = 1.0
    daily_sales: float = 2.0
    accumulated_sales: float = 105.0
    ad_exposure: float = 303284.5
    sns_mention_daily: float = 0.0
    promo_event_flag: int = 0

    class Config:
        extra = "ignore"


@router.post("/ticket_risk_selling")
def api_predict_ticket_risk(inputs: List[TicketRiskInput]):
    input_data = [inp.dict() for inp in inputs]
    preds = predict_ticket_risk(input_data)
    return {"risk_labels": np.array(preds).tolist()}


# ---------------------------
# 집계(산업 추이) 시각화 API 엔드포인트
# ---------------------------
@router.get("/genre_stats")
def api_get_genre_stats():
    stats = get_genre_stats()
    return stats

@router.get("/regional_stats")
def api_get_regional_stats():
    stats = get_regional_stats()
    return stats

@router.get("/venue_scale_stats")
def api_get_venue_scale_stats():
    stats = get_venue_scale_stats()
    return stats