from backend.AzureServiceModule.AzureSQLClient import execute_query
import pandas as pd

def get_genre_stats() -> dict:
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
    df.sort_values(by="genre", inplace=True)
    
    return {
        "genre_stats": {
            "genre": df["genre"].tolist(),
            "performance_count": df["performance_count"].astype(int).tolist(),
            "audience": df["audience"].astype(int).tolist(),
            "ticket_revenue": df["ticket_revenue"].astype(int).tolist()
        }
    }

def get_regional_stats() -> dict:
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
    df.sort_values(by="region", inplace=True)
    
    return {
        "regional_stats": {
            "region": df["region"].tolist(),
            "performance_count": df["performance_count"].astype(int).tolist(),
            "show_count": df["show_count"].astype(int).tolist(),
            "total_ticket_sales": df["total_ticket_sales"].astype(int).tolist(),
            "total_ticket_revenue": df["total_ticket_revenue"].astype(int).tolist()
        }
    }

def get_venue_scale_stats() -> dict:
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
    
    return {
        "venue_scale_stats": {
            "year": grouped["year"].astype(int).tolist(),
            "scale": grouped["scale"].tolist(),
            "performance_count": grouped["performance_count"].astype(int).tolist(),
            "total_ticket_sales": grouped["total_ticket_sales"].astype(int).tolist()
        }
    }

if __name__ == "__main__":
    # 테스트 호출
    print("==== GENRE STATS ====")
    print(get_genre_stats())
    
    print("\n==== REGIONAL STATS ====")
    print(get_regional_stats())
    
    print("\n==== VENUE SCALE STATS ====")
    print(get_venue_scale_stats())