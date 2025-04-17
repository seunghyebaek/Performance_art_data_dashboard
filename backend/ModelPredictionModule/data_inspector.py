# backend/ModelPredictionModule/data_inspector.py

import sys
from backend.AzureServiceModule.AzureSQLClient import execute_query
import pandas as pd

def get_all_user_tables() -> list:
    """
    SQL Server에서 현재 DB의 user table(일반 테이블) 목록을 가져옵니다.
    schema='dbo' 기준이며, system table 등은 제외합니다.
    """
    query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
      AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME;
    """
    df_tables = execute_query(query)
    table_list = df_tables["TABLE_NAME"].tolist()
    return table_list

def inspect_table(table_name: str, top_n=5):
    """
    주어진 테이블에서 상위 top_n개 레코드를 조회하고, 콘솔에 정보를 출력합니다.
    """
    query = f"SELECT TOP {top_n} * FROM dbo.[{table_name}];"  # 테이블명에 대괄호 포함(특수문자 대비)
    df = execute_query(query)
    
    print("=" * 80)
    print(f"[Table: {table_name}] 상위 {top_n}행 샘플")
    print(df)
    print("\n[Data Types]:")
    df.info(verbose=True)
    print("\n[기본 기술통계(숫자열 기준)]:")
    print(df.describe(include='number'))
    print("=" * 80, "\n")

def inspect_all_tables(top_n=5):
    """
    DB 내 모든 user table을 순회하며, 각 테이블별 상위 top_n개 행을 콘솔에 출력합니다.
    """
    table_list = get_all_user_tables()
    
    print("\n[검색된 테이블 목록]")
    for t in table_list:
        print(f" - {t}")
    
    print("\n--- 모든 테이블 샘플 조회 시작 ---\n")
    for t in table_list:
        inspect_table(t, top_n=top_n)

if __name__ == "__main__":
    # 기본적으로 top_n=5로 샘플을 확인합니다.
    # 필요하면 명령줄 인자로 개수를 조정 가능 (예: python data_inspector.py 10)
    if len(sys.argv) > 1:
        top_n = int(sys.argv[1])
    else:
        top_n = 5
    
    inspect_all_tables(top_n=top_n)
