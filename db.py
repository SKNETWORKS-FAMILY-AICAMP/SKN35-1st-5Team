import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

# 환경 변수 로드 (.env 파일에 DB 접속 정보 설정)
load_dotenv(Path(__file__).with_name(".env"))

DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_DATABASE", "cars_db") 

# TiDB / MySQL 연결 URL 구성 (PyMySQL 사용)
def _get_database_url() -> URL:
    """Build a safe MySQL/TiDB connection URL from environment variables."""
    required = {
        "DB_USERNAME": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_DATABASE": DB_NAME,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Missing database setting(s): {', '.join(missing)}")

    query = {"charset": "utf8mb4"}
    ssl_enabled = os.getenv("DB_SSL_ENABLED", "").lower()
    is_tidb_cloud = DB_HOST.endswith("tidbcloud.com")
    if ssl_enabled not in {"false", "0", "no"} and (ssl_enabled in {"true", "1", "yes"} or is_tidb_cloud):
        query.update(
            {
                "ssl_ca": os.getenv("DB_SSL_CA", certifi.where()),
                "ssl_verify_cert": "true",
                "ssl_verify_identity": "true",
            }
        )

    return URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        query=query,
    )


DATABASE_URL = _get_database_url()

def get_engine():
    """SQLAlchemy 엔진 객체를 반환합니다."""
    engine = create_engine(
        DATABASE_URL,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
    return engine

def init_database_tables():
    """
    데이터베이스에 필요한 테이블들을 생성합니다.
    테이블이 존재하지 않을 경우에만 생성되도록 구성되어 있습니다.
    """
    engine = get_engine()
    
    # 아래는 제가 테스트용으로 테이블 생성해 봤는데 회의후에 테이블 구조 바꿔야 하면 지우고 다시 하기 위해 DROP구문 넣어둔 겁니다.
    # with engine.begin() as conn:
    #     conn.execute(text("DROP TABLE IF EXISTS model_ranking_table;"))
    #     conn.execute(text("DROP TABLE IF EXISTS brand_ranking_table;"))
    #     conn.execute(text("DROP TABLE IF EXISTS ev_price_table;"))
    #     conn.execute(text("DROP TABLE IF EXISTS car_registration_table;"))
    #     conn.execute(text("DROP TABLE IF EXISTS ev_stations_table;"))
    #     conn.execute(text("DROP TABLE IF EXISTS faq_table;"))

    create_tables_sql = """
    -- 1. 전국 자동차 등록 현황 테이블
    CREATE TABLE IF NOT EXISTS car_registration_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        기준연월 VARCHAR(20),
        제조사구분 VARCHAR(20),
        제조사 VARCHAR(50),
        시도 VARCHAR(50),
        차종 VARCHAR(50),
        연료 VARCHAR(50),
        등록대수 INT
    );

    -- 2. 브랜드별 랭킹 테이블
    CREATE TABLE IF NOT EXISTS brand_ranking_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        기준연월 VARCHAR(20),
        제조사구분 VARCHAR(20),
        브랜드 VARCHAR(50),
        등록대수 INT,
        전월대비증가 INT
    );

    -- 3. 모델별 랭킹 테이블
    CREATE TABLE IF NOT EXISTS model_ranking_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        기준연월 VARCHAR(20),
        제조사구분 VARCHAR(20),
        브랜드 VARCHAR(50),
        차량이름 VARCHAR(100),
        연료 VARCHAR(50),
        등록대수 INT,
        전월대비증가 INT
    );

    -- 4. 전기차 가격 및 제원 테이블
    CREATE TABLE IF NOT EXISTS ev_price_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        브랜드 VARCHAR(50),
        모델명 VARCHAR(100),
        `차량가격(원)` BIGINT,
        `정부보조금(원)` BIGINT,
        `배터리용량(kWh)` FLOAT,
        `주행거리(km)` INT,
        `전비(km/kWh)` FLOAT
    );

    -- 5. 전기차 충전소 정보 테이블
    CREATE TABLE IF NOT EXISTS ev_stations_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        충전소명 VARCHAR(100),
        지역 VARCHAR(50),
        lat FLOAT,
        lon FLOAT,
        급속충전기수 INT,
        완속충전기수 INT,
        운영상태 VARCHAR(50)
    );

    -- 6. FAQ 테이블
    CREATE TABLE IF NOT EXISTS faq_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        카테고리 VARCHAR(50),
        질문 TEXT,
        답변 TEXT
    );
    """

    with engine.begin() as conn:
        for statement in create_tables_sql.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))

if __name__ == "__main__":
    init_database_tables()
    print("데이터베이스 테이블 초기화가 완료되었습니다.")
