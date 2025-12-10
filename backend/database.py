import sqlite3
import os  # 운영체제 경로 기능을 쓰기 위해 추가

# ---------------------------------------------------------
# [중요] DB 파일 위치를 현재 파일(database.py)과 같은 폴더로 고정
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "halla_cafeteria.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            menu TEXT,
            UNIQUE(date, type) 
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ DB 초기화 완료: {DB_PATH}")

def save_menus(menu_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = 0
    for item in menu_list:
        try:
            c.execute('''
                INSERT OR REPLACE INTO menus (date, type, menu)
                VALUES (?, ?, ?)
            ''', (item['date'], item['type'], item['menu']))
            count += 1
        except Exception as e:
            print(f"저장 중 에러: {e}")
            
    conn.commit()
    conn.close()
    print(f"💾 {count}개 데이터 저장 완료")

def get_all_menus():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM menus ORDER BY date, type")
    rows = c.fetchall()
    conn.close()
    return rows