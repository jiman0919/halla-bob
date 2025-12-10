import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [menus, setMenus] = useState([]);
  const [todayDate, setTodayDate] = useState('');     // 오늘 날짜 (YYYY.MM.DD)
  const [viewDate, setViewDate] = useState('');       // 현재 보고 있는 날짜 (YYYY.MM.DD)
  const [errorMsg, setErrorMsg] = useState(null);
  const [slideDirection, setSlideDirection] = useState('right'); // 애니메이션 방향

  useEffect(() => {
    // 1. 오늘 날짜 구하기
    const now = new Date();
    const formattedDate = formatDate(now);
    setTodayDate(formattedDate);
    setViewDate(formattedDate);

    // 2. 데이터 가져오기
    fetch("https://halla-bob-backend.onrender.com/menus")
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data)) {
          // 정렬 로직 (날짜 -> 식사유형)
          const mealPriority = { "조식": 1, "중식": 2, "석식": 3 };
          const sortedData = data.sort((a, b) => {
            if (a.date !== b.date) return a.date.localeCompare(b.date);
            return (mealPriority[a.type] || 4) - (mealPriority[b.type] || 4);
          });
          setMenus(sortedData);
          setErrorMsg(null);
        } else {
          setMenus([]);
          setErrorMsg(data.error || "데이터 형식 오류");
        }
      })
      .catch((error) => {
        setErrorMsg("서버 연결 실패 (백엔드 확인 필요)");
      });
  }, []);

  // --- 날짜 포맷 (YYYY.MM.DD) ---
  const formatDate = (dateObj) => {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
  };

  // --- 요일 구하기 (날짜 문자열을 받아서 요일 반환) ---
  const getDayOfWeek = (dateString) => {
    const days = ['(일)', '(월)', '(화)', '(수)', '(목)', '(금)', '(토)'];
    const parts = dateString.split('.');
    const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
    return days[dateObj.getDay()];
  };

  // --- 날짜 변경 핸들러 ---
  const changeDate = (offset) => {
    const parts = viewDate.split('.');
    const current = new Date(parts[0], parts[1] - 1, parts[2]);
    
    current.setDate(current.getDate() + offset);
    
    // 애니메이션 방향 설정 (다음날로 가면 오른쪽에서 등장, 전날은 왼쪽에서 등장)
    setSlideDirection(offset > 0 ? 'slide-in-right' : 'slide-in-left');
    setViewDate(formatDate(current));
  };

  // --- 필터링 ---
  const todayMenus = Array.isArray(menus) 
    ? menus.filter((item) => item.date.includes(todayDate)) 
    : [];

  const viewMenus = Array.isArray(menus)
    ? menus.filter((item) => item.date.includes(viewDate))
    : [];

  return (
    <div className="mobile-container">
      <header className="app-header">
        <h1>한라대 학식메뉴</h1>
      </header>

      {errorMsg && <div className="error-box">{errorMsg}</div>}

      {/* --- 섹션 1: 오늘의 학식 --- */}
      <section className="section-today">
        <h2 className="section-title">
          🔥 오늘의 학식 <span className="today-date">{todayDate} {getDayOfWeek(todayDate)}</span>
        </h2>
        
        <div className="today-list">
          {todayMenus.length > 0 ? (
            todayMenus.map((item) => (
              <div key={item.id} className={`menu-card ${item.type}`}>
                <div className="card-header">
                  <span className="badge">{item.type}</span>
                </div>
                <div className="menu-content">
                  {item.menu.split('\n').map((line, i) => <div key={i}>{line}</div>)}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-card">
              <p>😴 오늘은 학식이 없어요</p>
            </div>
          )}
        </div>
      </section>

      <hr className="divider" />

      {/* --- 섹션 2: 날짜별 메뉴 탐색 --- */}
      <section className="section-daily-nav">
        <h2 className="section-title">📅 날짜별 식단표</h2>
        
        {/* 네비게이터 */}
        <div className="date-navigator">
          <button className="nav-btn" onClick={() => changeDate(-1)}>◀</button>
          <span className="current-date-display">
            {viewDate} <span className="day-text">{getDayOfWeek(viewDate)}</span>
          </span>
          <button className="nav-btn" onClick={() => changeDate(1)}>▶</button>
        </div>

        {/* [중요] key={viewDate}를 넣어야 날짜가 바뀔 때마다 
          React가 div를 새로 그려서 애니메이션이 다시 실행됨 
        */}
        <div key={viewDate} className={`daily-menu-list ${slideDirection}`}>
          {viewMenus.length > 0 ? (
            viewMenus.map((item) => (
              <div key={item.id} className="daily-item">
                <div className="daily-type">
                  <span className={`mini-badge ${item.type}`}>{item.type}</span>
                </div>
                <div className="daily-menu-text">
                  {item.menu.split('\n').map((line, i) => <span key={i}>{line}<br/></span>)}
                </div>
              </div>
            ))
          ) : (
            <div className="no-data-day">
              <p>🍽️ 이 날짜의 식단 정보가 없습니다.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default App;
