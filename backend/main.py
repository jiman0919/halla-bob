from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import database
import crawler
import datetime

app = FastAPI()

# --- CORS 설정 ---
origins = [
    "https://halla-bob.vercel.app",
    "*"      
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# [핵심] 정해진 시간에 실행될 함수 (작업자)
# ---------------------------------------------------------
def scheduled_crawling_job():
    print(f"⏰ [주간 자동 크롤링 시작] {datetime.datetime.now()}")
    try:
        # 1. 크롤링 수행
        menus = crawler.get_halla_menu()
        if menus:
            # 2. DB 저장
            database.save_menus(menus)
            print(f"✅ [크롤링 완료] {len(menus)}개의 데이터 업데이트 됨")
        else:
            print("⚠️ 가져온 데이터가 없습니다.")
    except Exception as e:
        print(f"❌ 자동 크롤링 중 에러 발생: {e}")

# ---------------------------------------------------------
# [설정] 스케줄러 시작 (매주 월요일 06:00 실행)
# ---------------------------------------------------------
@app.on_event("startup")
def start_scheduler():
    database.init_db()
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    
    # 수정된 부분: day_of_week='mon' 추가 (월요일만 실행)
    scheduler.add_job(scheduled_crawling_job, 'cron', day_of_week='mon', hour=6, minute=0)
    
    scheduler.start()
    print("🚀 [시스템] 스케줄러가 시작되었습니다 (매주 월요일 06:00 실행)")

# --- API 라우터 ---

@app.get("/")
def read_root():
    return {"message": "한라대학교 학식 API 서버 (주간 자동화 적용됨)"}

@app.get("/menus")
def read_menus():
    try:
        rows = database.get_all_menus()
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "date": row[1],
                "type": row[2],
                "menu": row[3]
            })
        return result
    except Exception as e:
        return {"error": str(e)}

# (옵션) 강제 크롤링 버튼 (테스트용)
# 주소창에 http://127.0.0.1:8000/crawl 입력 시 즉시 실행
@app.get("/crawl")
def manual_crawl():
    scheduled_crawling_job()
    return {"message": "관리자 요청으로 크롤링을 수행했습니다."}
