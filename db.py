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

    insert_initial_faqs(engine)

def insert_initial_faqs(engine):
    """FAQ 샘플 데이터를 데이터베이스에 적재합니다."""
    faq_data = [
        {
            "카테고리": "차량 등록",
            "질문": "신차를 구입한 후 등록까지 며칠 이내에 해야 하나요?",
            "답변": "신차 신규 등록은 임시운행허가기간 내(통상 10일 이내)에 하셔야 과태료를 면할 수 있습니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "차량 명의를 변경할 때 필요한 서류가 무엇인가요?",
            "답변": "이전등록신청서, 양도증명서, 양도인 인감증명서(또는 본인서명사실확인서), 양수인 의무보험가입증명서 등이 필요합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "중고차를 구입한 경우 이전등록(명의변경)은 언제까지 해야 하나요?",
            "답변": "매매일로부터 15일 이내에 이전등록을 완료해야 과태료를 피할 수 있습니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "중고차 이전등록 시 필요한 서류는 무엇인가요?",
            "답변": "자동차등록증, 이전등록신청서, 양도증명서, 양도인·양수인 신분증(또는 위임장), 의무보험 가입증명서가 필요합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "차량 명의이전 시 보험은 언제 가입해야 하나요?",
            "답변": "이전등록 신청 전 또는 당일에 양수인 명의로 의무보험(책임보험)에 미리 가입되어 있어야 등록이 가능합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "자동차 명의를 공동명의로 등록하려면 어떻게 해야 하나요?",
            "답변": "공동명의자 모두의 신분증과 도장이 필요하며, 한 명이 방문할 경우 불참자의 위임장과 인감증명서(또는 서명사실확인서)를 지참해야 합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "차량을 말소등록(폐차)할 때는 어떤 서류가 필요한가요?",
            "답변": "자동차등록증, 신분증, 그리고 폐차장에서 발급해 주는 폐차인수증명서가 필요합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "자동차 주소지(사용본거지)가 변경되었을 때 변경등록은 언제까지 해야 하나요?",
            "답변": "이사한 날부터 30일 이내에 변경등록을 신청해야 하며, 전입신고 시 자동차 주소지 변경도 함께 신청할 수 있는 원스톱 서비스를 이용하면 편리합니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "타 지역 번호판을 달고 있는데, 전국 번호판(필름식 또는 페인트식)으로 교체할 수 있나요?",
            "답변": "네, 소유자 주소지 관할 차량등록사업소를 방문하여 번호판 교체 신청(등록번호판 재발급)을 하시면 전국 번호판으로 변경할 수 있습니다."
        },
        {
            "카테고리": "차량 등록",
            "질문": "자동차등록증을 분실했는데 재발급받으려면 어떻게 해야 하나요?",
            "답변": "신분증을 지참하여 가까운 시·군·구청이나 차량등록사업소에 직접 방문하거나, 정부24(gov.kr) 웹사이트를 통해 온라인으로 재발급받을 수 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 구매 보조금은 어떻게 신청하나요?",
            "답변": "지자체별 보조금 신청 기간에 맞춰 차량 계약 후 제조·판매사와 함께 무공해차 통합누리집을 통해 대행 신청하게 됩니다."
        },
        {
            "카테고리": "전기차",
            "질문": "공영주차장 이용 시 전기차 할인 혜택이 있나요?",
            "답변": "네, 지자체에 따라 공영주차장 요금 50~80% 감면 및 하이패스 통행료 할인 등의 혜택을 받을 수 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 보조금을 지원받은 후 의무운행기간 내에 차량을 판매하면 어떻게 되나요?",
            "답변": "보조금 지급일로부터 일정 기간(통상 2년) 의무운행기간을 채워야 하며, 기간 내 판매 시 잔여 기간에 따라 보조금이 환수되거나 구매자에게 권리가 승계될 수 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 충전기는 어떤 종류가 있으며 충전 시간은 얼마나 걸리나요?",
            "답변": "급속 충전기(약 30분~1시간 소요)와 완속 충전기(약 4~10시간 소요)로 나뉘며, 차량 배터리 용량과 충전기 출력에 따라 차이가 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "아파트나 주거지에 설치된 완속 충전기에서 다른 차가 자리를 차지하고 있으면 어떻게 하나요?",
            "답변": "충전완료 후 일정 시간이 지나도 차를 이동시키지 않는 경우 충전방해 금지법에 따라 과태료가 부과될 수 있으며, 관할 지자체나 안전신문고 앱을 통해 신고할 수 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 배터리 보증 기간과 주행거리는 어떻게 되나요?",
            "답변": "대다수 제조사에서 전기차 고전압 배터리에 대해 보통 8년 또는 16만 km 이내에서 보증 기간을 제공하며, 이 기간 내 성능이 일정 수준 이상 저하되면 무상 수리나 교체를 받을 수 있습니다."
        },
        {
            "카테고리": "전기차",
            "질문": "겨울철에 전기차 주행거리가 짧아지는 이유는 무엇인가요?",
            "답변": "저온에서 리튬이온 배터리의 효율이 떨어지고, 실내 난방을 위해 히터를 가동하면서 전력 소모가 급증하기 때문에 주행거리가 일시적으로 감소합니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 전용 번호판은 반드시 부착해야 하나요?",
            "답변": "네, 신규 등록하는 전기차는 하늘색 바탕에 태극문양과 EV 마크가 포함된 전기차 전용 번호판을 의무적으로 부착해야 합니다."
        },
        {
            "카테고리": "전기차",
            "질문": "전기차 정비는 일반 내연기관 차량과 어떻게 다른가요?",
            "답변": "엔진오일, 점화플러그 등의 소모품 교체가 필요 없어 유지보수가 편리하지만, 배터리, 모터, 전력제어장치 등 고전압 시스템은 전문 정비 인프라를 갖춘 서비스 센터에서 점검받아야 합니다."
        },
        {
            "카테고리": "전기차",
            "질문": "완속 충전 카드(로밍 카드)는 무엇이고 어떻게 발급받나요?",
            "답변": "다양한 충전 사업자의 충전기를 하나의 카드로 편리하게 이용할 수 있게 해주는 카드로, 환경부 공공충전환전 플랫폼이나 민간 충전 사업자 홈페이지에서 회원 가입 후 발급받을 수 있습니다."
        }
    ]

    df = pd.DataFrame(faq_data)
    
    # 이미 FAQ 데이터가 들어있는지 확인 후, 비어있을 때만 넣거나 append 실행
    # try:
    #     existing_df = pd.read_sql("SELECT COUNT(*) as cnt FROM faq_table", con=engine)
    #     if existing_df['cnt'][0] == 0:
    #         df.to_sql(name="faq_table", con=engine, if_exists="append", index=False)
    #         print("FAQ 샘플 데이터가 성공적으로 적재되었습니다!")
    #     else:
    #         print("FAQ 테이블에 이미 데이터가 존재하여 생략합니다.")
    # except Exception as e:
    #     print(f"FAQ 데이터 적재 중 확인 과정에서 예외 발생: {e}")

    try:
        df.to_sql(name="faq_table", con=engine, if_exists="replace", index=False)
        print("FAQ 샘플 데이터가 성공적으로 덮어씌워졌습니다!")
    except Exception as e:
        print(f"FAQ 데이터 적재 중 예외 발생: {e}")

if __name__ == "__main__":
    init_database_tables()
    print("데이터베이스 테이블 초기화가 완료되었습니다.")
