import os
from pathlib import Path

import certifi
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

# constants.py에서 상수 임포트
from sql import qna_table

# 환경 변수 로드 (.env 파일에 DB 접속 정보 설정)
load_dotenv(Path(__file__).with_name(".env"))

DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_DATABASE", "cars_db")


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
    engine = create_engine(
        DATABASE_URL,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
    return engine


def init_database_tables():
    engine = get_engine()

    with engine.begin() as conn:
        for statement in qna_table.CREATE_TABLES_SQL.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))

    insert_initial_faqs(engine)


def insert_initial_faqs(engine):
    df = pd.DataFrame(qna_table.INITIAL_FAQ_DATA)

    try:
        df.to_sql(name="faq", con=engine, if_exists="append", index=False)
        print("FAQ 데이터 적재 성공!")
    except Exception as e:
        print(f"FAQ 데이터 적재 중 예외 발생: {e}")


if __name__ == "__main__":
    init_database_tables()
    print("데이터베이스 초기화 스크립트 실행이 완료되었습니다.")