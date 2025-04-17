import os
import joblib
import pandas as pd
import numpy as np
from typing import List
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.preprocessing import label_binarize

from AzureServiceModule.AzureSQLClient import execute_query

FILE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(FILE_DIR, "models")

def load_model(model_name: str):
    """
    model_name: 예) 'xgb_reg_accumulated_sales_planning' (확장자 제외)
    models 폴더에서 해당 pkl 파일을 로드합니다.
    """
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    model = joblib.load(model_path)
    return model


# -----------------
# 1) 회귀 예측 함수들
# -----------------

def predict_acc_sales_planning(input_data: List[dict]) -> dict:
    """
    (기획 단계) 관객 수 예측
    모델 파일: xgb_reg_accumulated_sales_planning.pkl
    """
    model = load_model("xgb_reg_accumulated_sales_planning")
    df = pd.DataFrame(input_data)
    preds = model.predict(df)
    
    comparison_data = [
        {"performance_id": 101, "performance_name": "뮤지컬 캣츠", "actual": 2800, "predicted": float(preds[0])},
        {"performance_id": 102, "performance_name": "콘서트 아이유", "actual": 3000, "predicted": float(preds[0]) + 120},
        {"performance_id": 103, "performance_name": "오페라 카르멘", "actual": 2500, "predicted": float(preds[0]) - 80},
        {"performance_id": 104, "performance_name": "연극 연애혁명", "actual": 2900, "predicted": float(preds[0]) + 50},
        {"performance_id": 105, "performance_name": "무용 공연 불릿", "actual": 2700, "predicted": float(preds[0]) - 30}
    ]
    
    time_series_data = {
        "dates": ["2025-05-01", "2025-05-02", "2025-05-03", "2025-05-04", "2025-05-05"],
        "predicted_cumulative": [1000, 2000, float(preds[0]), float(preds[0]) + 150, float(preds[0]) + 300],
        "confidence_interval": {
            "lower": [950, 1900, float(preds[0]) - 20, float(preds[0]) + 130, float(preds[0]) + 280],
            "upper": [1050, 2100, float(preds[0]) + 20, float(preds[0]) + 170, float(preds[0]) + 320]
        }
    }
    
    capacity_scatter = {
        "data": [
            {"performance_id": 101, "capacity": 500, "predicted_sales": float(preds[0]), "genre": "뮤지컬"},
            {"performance_id": 102, "capacity": 750, "predicted_sales": float(preds[0]) + 50, "genre": "뮤지컬"},
            {"performance_id": 103, "capacity": 600, "predicted_sales": float(preds[0]) - 30, "genre": "뮤지컬"}
        ]
    }
    
    return {
        "predictions": preds.tolist(),
        "comparison": {"performances": comparison_data},
        "capacity_scatter": capacity_scatter,
        "time_series": time_series_data
    }


def predict_acc_sales_selling(input_data: List[dict]) -> dict:
    """
    (판매 단계) 관객 수 예측
    모델 파일: xgb_reg_accumulated_sales_selling.pkl
    """
    model = load_model("xgb_reg_accumulated_sales_selling")
    df = pd.DataFrame(input_data)
    preds = model.predict(df)
    
    time_series_data = {
        "dates": ["2025-06-01", "2025-06-02", "2025-06-03", "2025-06-04"],
        "actual_cumulative": [1100, 2000, 3000, float(preds[0])],
        "predicted_cumulative": [1150, 2050, 3100, float(preds[0])]
    }
    
    capacity_scatter = {
        "data": [
            {"performance_id": 201, "capacity": 500, "accumulated_sales": float(preds[0])},
            {"performance_id": 202, "capacity": 750, "accumulated_sales": float(preds[0]) - 100},
            {"performance_id": 203, "capacity": 600, "accumulated_sales": float(preds[0]) + 50}
        ]
    }
    
    comparison_data = [
        {"performance_id": 201, "performance_name": "뮤지컬 이프댄", "actual": 1200, "predicted": float(preds[0])},
        {"performance_id": 202, "performance_name": "콘서트 아이유", "actual": 950, "predicted": float(preds[0]) - 40},
        {"performance_id": 203, "performance_name": "오페라 카르멘", "actual": 1100, "predicted": float(preds[0]) + 30}
    ]
    
    return {
        "predictions": preds.tolist(),
        "time_series": time_series_data,
        "capacity_scatter": capacity_scatter,
        "comparison": {"performances": comparison_data}
    }


def predict_roi_bep_planning(input_data: List[dict]) -> dict:
    """
    (기획 단계) 손익 예측
    모델 파일: xgb_reg_roi_bep_planning.pkl
    """
    model = load_model("xgb_reg_roi_bep_planning")
    df = pd.DataFrame(input_data)
    preds = model.predict(df)
    
    roi_bep_detail = {
        "total_revenue": 35000000,
        "total_cost": 42000000,
        "fixed_cost": 60000000,
        "variable_cost_rate": 0.2
    }
    
    roi_time_series = {
        "dates": ["시뮬레이션1", "시뮬레이션2", "시뮬레이션3", "시뮬레이션4", "시뮬레이션5"],
        "roi_values": [-0.85, -0.84, -0.83, float(preds[0][0]), -0.86]
    }
    
    roi_distribution = {
        "roi_values": [-0.85, -0.84, -0.83, float(preds[0][0]), -0.86],
        "bep_values": [3400, 3410, 3420, float(preds[0][1]), 3430]
    }
    
    return {
        "predictions": preds.tolist(),
        "roi_bep_detail": roi_bep_detail,
        "roi_time_series": roi_time_series,
        "roi_distribution": roi_distribution
    }


def predict_roi_bep_selling(input_data: List[dict]) -> dict:
    """
    (판매 단계) 손익 예측
    모델 파일: xgb_reg_roi_bep_selling.pkl
    """
    model = load_model("xgb_reg_roi_bep_selling")
    df = pd.DataFrame(input_data)
    preds = model.predict(df)
    
    comparison_data = {
        "actual": {
            "accumulated_sales": 50000,
            "total_revenue": 40000000,
            "total_cost": 45000000
        },
        "predicted": {
            "accumulated_sales": 50000,
            "roi": float(preds[0][0]),
            "bep": float(preds[0][1])
        }
    }
    
    time_series_data = {
        "dates": ["2025-07-01", "2025-07-02", "2025-07-03"],
        "actual_cumulative": [15000, 35000, 50000],
        "predicted_cumulative": [15500, 36000, 50000],
        "confidence_interval": {
            "lower": [15000, 34000, 48000],
            "upper": [16000, 37000, 52000]
        }
    }
    
    return {
        "predictions": preds.tolist(),
        "comparison": comparison_data,
        "time_series": time_series_data
    }


# 분류: 티켓 판매 위험 예측 (조기 경보)

# def compute_roc_pr(y_true, y_proba, num_classes=3):
#     """
#     ROC/PR 커브 계산
#     """
#     y_true_bin = label_binarize(y_true, classes=list(range(num_classes)))
#     roc_data = []
#     pr_data = []
#     for i in range(num_classes):
#         fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
#         precision, recall, _ = precision_recall_curve(y_true_bin[:, i], y_proba[:, i])
#         roc_data.append({
#             "class": i,
#             "fpr": fpr.tolist(),
#             "tpr": tpr.tolist()
#         })
#         pr_data.append({
#             "class": i,
#             "precision": precision.tolist(),
#             "recall": recall.tolist()
#         })
#     return {"roc_curve": roc_data, "pr_curve": pr_data}


def predict_ticket_risk(input_data: List[dict]) -> dict:
    """
    (판매 단계) 티켓 위험 예측 분류
    모델 파일: rf_cls_ticket_risk.pkl
    """
    model = load_model("rf_cls_ticket_risk")
    df = pd.DataFrame(input_data)
    preds = model.predict(df)
    
    try:
        pred_proba = model.predict_proba(df)
    except:
        pred_proba = np.full((df.shape[0], 3), 1/3)

    # (이진분류 대응, 등등) -> 스킵...

    # dummy ground truth
    # y_true = np.array([0,1,2])  # 임시
    # evaluation_curves = compute_roc_pr(y_true, pred_proba, num_classes=3)
    
    booking_rate = input_data[0].get("booking_rate", 0)
    if booking_rate >= 75:
        warning_text = "안정 (저위험)"
    elif booking_rate >= 60:
        warning_text = "중위험"
    else:
        warning_text = "고위험"
    
    return {
        "risk_labels": preds.tolist(),
        "risk_detail": {
            "current_booking_rate": booking_rate,
            "target_booking_rate": 75,
            "warning": warning_text
        }}
    #     "evaluation_curves": evaluation_curves
    # }


# -----------------------------------------
# DB 버전: 집계 시각화 데이터 (실제 호출용)
# -----------------------------------------

def get_genre_stats_db() -> dict:
    """
    DB에서 가져오는 장르별 통계
    """
    query = "SELECT * FROM dbo.genre_stats_tb;"
    df = execute_query(query)
    df.rename(columns={
        "장르": "genre",
        "개막편수": "performance_count",
        "관객수": "audience",
        "매출액": "ticket_revenue"
    }, inplace=True)
    use_cols = ["genre", "performance_count", "audience", "ticket_revenue"]
    df = df[use_cols].fillna(0)
    # groupby or skip if already aggregated
    grouped = df.groupby("genre", as_index=False).sum()
    grouped.sort_values(by="genre", inplace=True)
    
    return {
        "genre_stats": {
            "genre": grouped["genre"].tolist(),
            "performance_count": grouped["performance_count"].astype(int).tolist(),
            "audience": grouped["audience"].astype(int).tolist(),
            "ticket_revenue": grouped["ticket_revenue"].astype(int).tolist()
        }
    }


def get_regional_stats_db() -> dict:
    """
    DB에서 가져오는 지역별 통계
    """
    query = "SELECT * FROM dbo.region_stats_tb;"
    df = execute_query(query)
    df.rename(columns={
        "지역명": "region",
        "공연건수": "performance_count",
        "상연횟수": "show_count",
        "총티켓판매수": "total_ticket_sales",
        "총티켓판매액": "total_ticket_revenue"
    }, inplace=True)
    use_cols = ["region", "performance_count", "show_count", "total_ticket_sales", "total_ticket_revenue"]
    df = df[use_cols].fillna(0)
    grouped = df.groupby("region", as_index=False).sum()
    grouped.sort_values(by="region", inplace=True)
    
    return {
        "regional_stats": {
            "region": grouped["region"].tolist(),
            "performance_count": grouped["performance_count"].astype(int).tolist(),
            "show_count": grouped["show_count"].astype(int).tolist(),
            "total_ticket_sales": grouped["total_ticket_sales"].astype(int).tolist(),
            "total_ticket_revenue": grouped["total_ticket_revenue"].astype(int).tolist()
        }
    }


def get_venue_scale_stats_db() -> dict:
    """
    DB에서 가져오는 공연장 규모별 통계 (2023/2024)
    """
    query = "SELECT * FROM dbo.facility_stats_tb;"
    df = execute_query(query)
    df.rename(columns={
        "연도": "year",
        "규모": "scale",
        "공연건수": "performance_count",
        "총티켓판매수": "total_ticket_sales"
    }, inplace=True)
    use_cols = ["year", "scale", "performance_count", "total_ticket_sales"]
    df = df[use_cols].fillna(0)
    grouped = df.groupby(["year", "scale"], as_index=False).sum()
    grouped.sort_values(by=["year", "scale"], inplace=True)
    
    # 더미 예시처럼 2023 + 2024 이어붙이기
    df_2023 = grouped[grouped["year"] == 2023].sort_values(by="scale")
    df_2024 = grouped[grouped["year"] == 2024].sort_values(by="scale")
    year_list = df_2023["year"].astype(int).tolist() + df_2024["year"].astype(int).tolist()
    scale_list = df_2023["scale"].tolist() + df_2024["scale"].tolist()
    perf_list = df_2023["performance_count"].astype(int).tolist() + df_2024["performance_count"].astype(int).tolist()
    sales_list = df_2023["total_ticket_sales"].astype(int).tolist() + df_2024["total_ticket_sales"].astype(int).tolist()
    
    return {
        "venue_scale_stats": {
            "year": year_list,
            "scale": scale_list,
            "performance_count": perf_list,
            "total_ticket_sales": sales_list
        }
    }


# ------------------------------------
# 더미 버전: ODBC 드라이버 없이 테스트할 수 있는 집계 데이터 (실제 집계와 동일 결과로 설정)
# ------------------------------------
def get_genre_stats() -> dict:
    """
    장르별 통계 - 더미 버전을 '실제 DB 결과'와 동일하게 갱신.
    """
    return {
        "genre_stats": {
            "genre": [
                "대중무용",
                "대중음악",
                "무용(서양/한국무용)",
                "뮤지컬",
                "복합",
                "서양음악(클래식)",
                "서커스/마술",
                "연극",
                "한국음악(국악)"
            ],
            "performance_count": [
                115,
                7586,
                1652,
                5963,
                862,
                15845,
                1359,
                5399,
                2556
            ],
            "audience": [
                74897,
                11528584,
                1196316,
                15868658,
                459707,
                6379810,
                1375820,
                5469736,
                865332
            ],
            "ticket_revenue": [
                5232114900,
                1337257477586,
                39483012874,
                923351724391,
                6150390882,
                201011077618,
                68307452991,
                135460853742,
                9751860962
            ]
        }
    }


def get_regional_stats() -> dict:
    """
    지역별 통계 - 더미 버전을 '실제 DB 결과'와 동일하게 갱신.
    """
    return {
        "regional_stats": {
            "region": [
                "강원도","경기","경기/인천","경남","경북","경상도","광주","대구","대전","부산",
                "서울","세종","울산","인천","전남","전라도","전북","제주도","충남","충북","충청도","합계"
            ],
            "performance_count": [
                1061,6200,7682,1564,1241,9023,1137,2699,1551,2825,
                23196,363,694,1482,724,2908,1047,574,1026,613,3553,47997
            ],
            "show_count": [
                2023,20085,24338,4517,2446,30292,4157,10212,5876,10499,
                156078,648,2618,4253,3051,10217,3009,3699,2135,2386,11045,237692
            ],
            "total_ticket_sales": [
                582917,4561151,5977633,877624,758169,6397471,807256,2067285,826402,2234348,
                26284380,196873,460045,1416482,400945,1781171,572970,279199,567710,325104,1916089,43218860
            ],
            "total_ticket_revenue": [
                27478563671,209759994957,323572313608,38098318991,23892649690,370460857349,46550414450,117366940722,51950324061,172433773289,
                1812089619145,6973849560,18669174657,113812318651,13269617790,88445301773,28625269533,9396123030,17660121674,17978892075,94563187370,2726005965946
            ]
        }
    }


def get_venue_scale_stats() -> dict:
    """
    공연장 규모별 통계 - 더미 버전을 '실제 DB 결과'와 동일하게 갱신.
    """
    return {
        "venue_scale_stats": {
            "year": [
                2023,2023,2023,2023,2023,2023,2023,
                2024,2024,2024,2024,2024,2024,2024
            ],
            "scale": [
                "1,000~5,000석 미만","10,000석 이상","1~300석 미만","300~500석 미만","5,000~10,000석 미만","500~1,000석 미만","좌석 미상",
                "1,000~5,000석 미만","10,000석 이상","1~300석 미만","300~500석 미만","5,000~10,000석 미만","500~1,000석 미만","좌석 미상"
            ],
            "performance_count": [
                4388,196,11253,5207,180,5331,2726,
                3735,86,6616,3742,47,3910,580
            ],
            "total_ticket_sales": [
                9238945,3706546,3908329,3135249,882933,3913562,1251977,
                7293316,1280626,2845973,2353712,291825,2906755,209112
            ]
        }
    }


# # ------------------------------------
# # (구) 더미 버전: 임시로 사용하던 집계 데이터
# # ------------------------------------


# def get_genre_stats() -> dict:
#     """
#     더미 버전 (사용자 요청에 따라 유지)
#     """
#     return {
#         "genre_stats": {
#             "genre": ["뮤지컬", "연극", "서양음악(클래식)", "대중음악", "무용(서양/한국)", "한국음악(국악)", "서커스/마술", "복합"],
#             "performance_count": [3006, 2932, 8199, 3970, 840, 1356, 835, 440],
#             "audience": [7831448, 2836558, 3290415, 6302709, 606737, 436947, 692155, 225613],
#             "ticket_revenue": [465122497, 73411508, 100996136, 756977444, 20633422, 4869454, 28565775, 2799943]
#         }
#     }

# def get_regional_stats() -> dict:
#     """
#     더미 버전 (사용자 요청에 따라 유지)
#     """
#     return {
#         "regional_stats": {
#             "region": ["서울", "경기", "부산", "대구", "인천"],
#             "performance_count": [9966, 2917, 1311, 1279, 687],
#             "show_count": [82160, 10807, 5429, 5146, 2231],
#             "total_ticket_sales": [13384094, 2549324, 1062750, 1002533, 823153],
#             "total_ticket_revenue": [946566611, 127171128, 82282070, 56503689, 76098489]
#         }
#     }

# def get_venue_scale_stats() -> dict:
#     """
#     더미 버전 (사용자 요청에 따라 유지)
#     """
#     year_2023 = [2023] * 7
#     scales = ["0석(좌석미상)", "1~300석 미만", "300~500석 미만", "500~1,000석 미만",
#               "1,000~5,000석 미만", "5,000~10,000석 미만", "10,000석 이상"]
#     perf_count_2023 = [1038, 6840, 4195, 4312, 3792, 112, 115]
#     ticket_sales_2023 = [562122, 3395810, 2720965, 3296964, 8277630, 666529, 2048869]
    
#     year_2024 = [2024] * 7
#     perf_count_2024 = [1493, 7147, 4135, 4558, 4038, 131, 132]
#     ticket_sales_2024 = [898841, 3429763, 2762187, 3504875, 8227156, 734900, 2682816]
    
#     return {
#         "venue_scale_stats": {
#             "year": year_2023 + year_2024,
#             "scale": scales + scales,
#             "performance_count": perf_count_2023 + perf_count_2024,
#             "total_ticket_sales": ticket_sales_2023 + ticket_sales_2024
#         }
#     }


if __name__ == "__main__":
    # 간단 테스트
    import pprint
    
    print("=== DB 버전: 장르별 ===")
    pprint.pprint(get_genre_stats_db())
    print("\n=== DB 버전: 지역별 ===")
    pprint.pprint(get_regional_stats_db())
    print("\n=== DB 버전: 규모별 ===")
    pprint.pprint(get_venue_scale_stats_db())
    
    print("\n=== 더미 버전: 장르별 ===")
    pprint.pprint(get_genre_stats())
    print("\n=== 더미 버전: 지역별 ===")
    pprint.pprint(get_regional_stats())
    print("\n=== 더미 버전: 규모별 ===")
    pprint.pprint(get_venue_scale_stats())
