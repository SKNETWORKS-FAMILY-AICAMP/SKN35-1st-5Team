import os
from pathlib import Path
import certifi
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
import pandas as pd

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
    데이터베이스에 필요한 테이블들이 없을 경우에만 생성합니다.
    (테이블 삭제는 DB 관리 툴에서 수동으로 처리)
    """
    engine = get_engine()
    
    create_tables_sql = """
    -- 자동차 등록 현황
    CREATE TABLE IF NOT EXISTS car_registration (
        regist_id VARCHAR(255) NOT NULL,
        company_type VARCHAR(255),
        company_name VARCHAR(255),
        model_name VARCHAR(255),
        count_car_month VARCHAR(255),
        standard_month VARCHAR(255) NOT NULL,
        PRIMARY KEY (regist_id)
    );

    -- 브랜드 랭킹
    CREATE TABLE IF NOT EXISTS car_brand_rank (
        brand_id VARCHAR(255) NOT NULL,
        regist_id VARCHAR(255) NOT NULL,
        compare_car_month VARCHAR(255),
        brand_standard_month VARCHAR(255) NOT NULL,
        brand_name VARCHAR(255) NOT NULL,
        PRIMARY KEY (brand_id, regist_id),
        CONSTRAINT FK_car_registration_TO_car_brand_rank
            FOREIGN KEY (regist_id)
            REFERENCES car_registration(regist_id)
    );

    -- 모델 랭킹
    CREATE TABLE IF NOT EXISTS car_model_ranking (
        model_id VARCHAR(255) NOT NULL,
        regist_id VARCHAR(255) NOT NULL,
        compare_car_month VARCHAR(255),
        standard_month VARCHAR(255) NOT NULL,
        brand_name VARCHAR(255),
        PRIMARY KEY (model_id, regist_id),
        CONSTRAINT FK_car_registration_TO_car_model_ranking
            FOREIGN KEY (regist_id)
            REFERENCES car_registration(regist_id)
    );

    -- 리뷰
    CREATE TABLE IF NOT EXISTS review (
        review_id VARCHAR(255) NOT NULL,
        model_id VARCHAR(255) NOT NULL,
        regist_id VARCHAR(255) NOT NULL,
        brand_name_review VARCHAR(255),
        PRIMARY KEY (review_id)
    );

    -- 리뷰 상세 (review와 review_id2로 조인)
    CREATE TABLE IF NOT EXISTS total_review (
        total_review_id VARCHAR(255) NOT NULL,
        review_id2 VARCHAR(255) NOT NULL,
        total_review_title VARCHAR(255),
        total_review_content TEXT,
        total_score VARCHAR(255),
        domain_type VARCHAR(255),
        PRIMARY KEY (total_review_id)
    );

    -- FAQ
    CREATE TABLE IF NOT EXISTS faq (
        faq_id INT AUTO_INCREMENT NOT NULL,
        question VARCHAR(255),
        answer TEXT, 
        PRIMARY KEY (faq_id)
    );

    -- 7. QnA 테이블
    """

    with engine.begin() as conn:
        for statement in create_tables_sql.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))

    insert_initial_faqs(engine)

def insert_initial_faqs(engine):
    faq_data = [
        {
            "question": "신차를 구입한 후 등록까지 며칠 이내에 해야 하나요?",
            "answer": "신차 신규 등록은 임시운행허가기간 내(통상 10일 이내)에 하셔야 과태료를 면할 수 있습니다."
        },
        {
            "question": "차량 명의를 변경할 때 필요한 서류가 무엇인가요?",
            "answer": "이전등록신청서, 양도증명서, 양도인 인감증명서(또는 본인서명사실확인서), 양수인 의무보험가입증명서 등이 필요합니다."
        },
        {
            "question": "중고차를 구입한 경우 이전등록(명의변경)은 언제까지 해야 하나요?",
            "answer": "매매일로부터 15일 이내에 이전등록을 완료해야 과태료를 피할 수 있습니다."
        },
        {
            "question": "중고차 이전등록 시 필요한 서류는 무엇인가요?",
            "answer": "자동차등록증, 이전등록신청서, 양도증명서, 양도인·양수인 신분증(또는 위임장), 의무보험 가입증명서가 필요합니다."
        },
        {
            "question": "차량 명의이전 시 보험은 언제 가입해야 하나요?",
            "answer": "이전등록 신청 전 또는 당일에 양수인 명의로 의무보험(책임보험)에 미리 가입되어 있어야 등록이 가능합니다."
        },
        {
            "question": "자동차 명의를 공동명의로 등록하려면 어떻게 해야 하나요?",
            "answer": "공동명의자 모두의 신분증과 도장이 필요하며, 한 명이 방문할 경우 불참자의 위임장과 인감증명서(또는 서명사실확인서)를 지참해야 합니다."
        },
        {
            "question": "차량을 말소등록(폐차)할 때는 어떤 서류가 필요한가요?",
            "answer": "자동차등록증, 신분증, 그리고 폐차장에서 발급해 주는 폐차인수증명서가 필요합니다."
        },
        {
            "question": "자동차 주소지(사용본거지)가 변경되었을 때 변경등록은 언제까지 해야 하나요?",
            "answer": "이사한 날부터 30일 이내에 변경등록을 신청해야 하며, 전입신고 시 자동차 주소지 변경도 함께 신청할 수 있는 원스톱 서비스를 이용하면 편리합니다."
        },
        {
            "question": "타 지역 번호판을 달고 있는데, 전국 번호판(필름식 또는 페인트식)으로 교체할 수 있나요?",
            "answer": "네, 소유자 주소지 관할 차량등록사업소를 방문하여 번호판 교체 신청(등록번호판 재발급)을 하시면 전국 번호판으로 변경할 수 있습니다."
        },
        {
            "question": "자동차등록증을 분실했는데 재발급받으려면 어떻게 해야 하나요?",
            "answer": "신분증을 지참하여 가까운 시·군·구청이나 차량등록사업소에 직접 방문하거나, 정부24(gov.kr) 웹사이트를 통해 온라인으로 재발급받을 수 있습니다."
        }
    ]

    df = pd.DataFrame(faq_data)
    
    try:
        df.to_sql(name="faq", con=engine, if_exists="append", index=False)
        print("FAQ 데이터 적재 성공!")
    except Exception as e:
        print(f"FAQ 데이터 적재 중 예외 발생: {e}")



if __name__ == "__main__":
    init_database_tables()
    print("데이터베이스 초기화 스크립트 실행이 완료되었습니다.")