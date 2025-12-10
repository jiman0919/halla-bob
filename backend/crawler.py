import requests
from bs4 import BeautifulSoup
import re
import database  # 같은 폴더에 있는 database.py를 불러옵니다

def get_halla_menu():
    """
    한라대학교 학식 사이트에서 메뉴를 크롤링하는 함수
    """
    url = "https://www.halla.ac.kr/kr/211/subview.do"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 식단 영역 찾기
        diet_area = soup.find('div', id='dietInfoArea')
        if not diet_area:
            print("❌ 식단 영역(dietInfoArea)을 찾을 수 없습니다.")
            return []

        table = diet_area.find('table')
        if not table:
            print("❌ 테이블을 찾을 수 없습니다.")
            return []

        # 2. 날짜 추출 (헤더 처리)
        headers = table.select("thead tr th")
        dates = []
        
        # 주말(토, 일) 제외하고 날짜만 리스트에 담기
        for th in headers:
            text = th.get_text(strip=True)
            if re.search(r'\d{4}\.\d{2}\.\d{2}', text):
                if "(토)" in text or "(일)" in text:
                    continue
                dates.append(text)

        # 3. 메뉴 추출 (본문 처리)
        temp_data = []
        rows = table.select("tbody tr")
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) < 2:
                continue
            
            meal_type = cells[0].get_text(strip=True) # 조식, 중식, 석식
            menu_cells = cells[1:]
            
            # 날짜 개수만큼 반복하며 메뉴 매칭
            for i, date in enumerate(dates):
                if i < len(menu_cells):
                    menu_text = menu_cells[i].get_text(separator="\n", strip=True)
                    
                    # 메뉴가 비어있으면 표시
                    if not menu_text:
                        menu_text = "메뉴 없음"
                    
                    temp_data.append({
                        "date": date,
                        "type": meal_type,
                        "menu": menu_text
                    })

        # 4. 정렬 (날짜순 -> 아침/점심/저녁 순)
        meal_order = {"조식": 1, "중식": 2, "석식": 3}
        sorted_menu_data = sorted(
            temp_data, 
            key=lambda x: (x['date'], meal_order.get(x['type'], 4))
        )

        return sorted_menu_data

    except Exception as e:
        print(f"❌ 크롤링 중 오류 발생: {e}")
        return []

def main():
    """
    실제 실행되는 메인 함수
    """
    # 1. DB 초기화 (테이블이 없으면 생성)
    database.init_db()

    # 2. 크롤링 수행
    print("🍱 한라대학교 학식 데이터 수집 시작...")
    menus = get_halla_menu()
    
    if menus:
        print(f"✅ 크롤링 성공! 총 {len(menus)}개의 메뉴를 찾았습니다.")
        
        # 3. DB에 저장 (database.py의 함수 호출)
        database.save_menus(menus)
        
        print("🎉 모든 작업이 완료되었습니다.")
        
        # (선택사항) 잘 들어갔나 확인용 출력
        print("\n[저장된 데이터 미리보기]")
        saved_data = database.get_all_menus()
        for i, row in enumerate(saved_data):
            if i >= 5: break # 5개만 출력
            print(f" - {row[1]} | {row[2]} | {row[3][:10]}...")
            
    else:
        print("⚠️ 수집된 데이터가 없습니다. 사이트를 확인해보세요.")

if __name__ == "__main__":
    main()