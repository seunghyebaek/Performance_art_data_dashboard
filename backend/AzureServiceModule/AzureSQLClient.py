# backend/AzureServiceModule/AzureSQLClient.py

import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import urllib.parse

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
db_id = os.getenv("AZURE_SQL_ID")
db_password = os.getenv("AZURE_SQL_PASSWORD")
db_endpoint = os.getenv("AZURE_SQL_ENDPOINT")
db_name = os.getenv("AZURE_SQL_DB")

# DSN-less 연결 문자열 구성
connection_string = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server=tcp:{db_endpoint},1433;"
    f"Database={db_name};"
    f"Uid={db_id};"
    f"Pwd={db_password};"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

# 전체 연결 문자열을 URL 인코딩
params = urllib.parse.quote_plus(connection_string)

# SQLAlchemy 엔진 생성 - odbc_connect 파라미터 사용
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

def execute_query(query: str) -> pd.DataFrame:
    """
    주어진 SQL 쿼리를 실행하여 결과를 pandas DataFrame으로 반환합니다.
    engine.raw_connection()을 사용하여 DBAPI 연결 객체를 명시적으로 닫습니다.
    """
    conn = engine.raw_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df
