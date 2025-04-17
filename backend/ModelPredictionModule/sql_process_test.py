# analysis_module.py  (예시 파일명)

import pandas as pd
from backend.AzureServiceModule.AzureSQLClient import execute_query

def get_genre_stats() -> dict:
    """
    장르별 통계 분석 - 장르별 공연 건수(performance_count), 관객 수(audience), 티켓 매출(ticket_revenue)
    DB 테이블: genre_stats_tb
    더미 예시와 동일 구조:
      {
        "genre_stats": {
            "genre": [...],
            "performance_count": [...],
            "audience": [...],
            "ticket_revenue": [...]
        }
      }
    """
    # 1) DB 조회
    query = "SELECT * FROM dbo.genre_stats_tb;"
    df = execute_query(query)

    # 2) 컬럼 rename
    df.rename(columns={
        "장르": "genre",
        "개막편수": "performance_count",
        "관객수": "audience",
        "매출액": "ticket_revenue"
    }, inplace=True)

    # 3) 필요한 컬럼만
    use_cols = ["genre", "performance_count", "audience", "ticket_revenue"]
    df = df[use_cols].fillna(0)

    # 4) 장르별 합계(또는 평균). DB에 이미 집계되어 있다면 skip 가능
    grouped = df.groupby("genre", as_index=False).sum()

    # 5) 장르명 정렬
    grouped.sort_values(by="genre", inplace=True)

    # 6) 딕셔너리 형태로 리턴
    return {
        "genre_stats": {
            "genre": grouped["genre"].tolist(),
            "performance_count": grouped["performance_count"].astype(int).tolist(),
            "audience": grouped["audience"].astype(int).tolist(),
            "ticket_revenue": grouped["ticket_revenue"].astype(int).tolist()
        }
    }

def get_regional_stats() -> dict:
    """
    지역별 통계 분석 - 공연 건수(performance_count), 회차(show_count), 티켓 판매(total_ticket_sales),
    티켓 매출(total_ticket_revenue)
    DB 테이블: region_stats_tb
    더미 예시와 동일 구조:
      {
        "regional_stats": {
            "region": [...],
            "performance_count": [...],
            "show_count": [...],
            "total_ticket_sales": [...],
            "total_ticket_revenue": [...]
        }
      }
    """
    # 1) DB 조회
    query = "SELECT * FROM dbo.region_stats_tb;"
    df = execute_query(query)

    # 2) 컬럼 rename
    df.rename(columns={
        "지역명": "region",
        "공연건수": "performance_count",
        "상연횟수": "show_count",
        "총티켓판매수": "total_ticket_sales",
        "총티켓판매액": "total_ticket_revenue"
    }, inplace=True)

    # 3) 필요한 컬럼만
    use_cols = ["region", "performance_count", "show_count", "total_ticket_sales", "total_ticket_revenue"]
    df = df[use_cols].fillna(0)

    # 4) 지역별 합산
    grouped = df.groupby("region", as_index=False).sum()

    # 5) 정렬
    grouped.sort_values(by="region", inplace=True)

    # 6) 딕셔너리 변환
    return {
        "regional_stats": {
            "region": grouped["region"].tolist(),
            "performance_count": grouped["performance_count"].astype(int).tolist(),
            "show_count": grouped["show_count"].astype(int).tolist(),
            "total_ticket_sales": grouped["total_ticket_sales"].astype(int).tolist(),
            "total_ticket_revenue": grouped["total_ticket_revenue"].astype(int).tolist()
        }
    }

def get_venue_scale_stats() -> dict:
    """
    공연장 규모별 통계 분석
    DB 테이블: facility_stats_tb
    더미 예시와 동일 구조:
      {
        "venue_scale_stats": {
            "year": [2023, ..., 2023, 2024, ..., 2024],
            "scale": [...],
            "performance_count": [...],
            "total_ticket_sales": [...]
        }
      }

    여기서는 2023, 2024 두 연도만 있다고 가정하고,
    year=2023 / year=2024 그룹을 이어붙여 더미 예시처럼 7+7=14개 형식으로 반환.
    """
    # 1) DB 조회
    query = "SELECT * FROM dbo.facility_stats_tb;"
    df = execute_query(query)

    # 2) rename
    df.rename(columns={
        "연도": "year",
        "규모": "scale",
        "공연건수": "performance_count",
        "총티켓판매수": "total_ticket_sales"
    }, inplace=True)

    use_cols = ["year", "scale", "performance_count", "total_ticket_sales"]
    df = df[use_cols].fillna(0)

    # 3) (연도, 규모)로 groupby
    grouped = df.groupby(["year", "scale"], as_index=False).sum()

    # 4) 2023 / 2024만 필터 (필요시 존재하는 모든 연도 loop)
    df_2023 = grouped[grouped["year"] == 2023].sort_values(by="scale")
    df_2024 = grouped[grouped["year"] == 2024].sort_values(by="scale")

    # 5) 이어붙이기
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


if __name__ == "__main__":
    # 테스트 호출
    # python -m backend.ModelPredictionModule.analysis_module
    import pprint

    print("==== GENRE STATS ====")
    pprint.pprint(get_genre_stats())

    print("\n==== REGIONAL STATS ====")
    pprint.pprint(get_regional_stats())

    print("\n==== VENUE SCALE STATS ====")
    pprint.pprint(get_venue_scale_stats())
