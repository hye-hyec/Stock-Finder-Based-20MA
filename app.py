import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="NASDAQ Scanner Pro", page_icon="📈", layout="wide")

# --- 🖤 고급스러운 트레이딩 룸 느낌의 딥다크 CSS ---
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #0d1117 !important;
    color: #ffffff !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
}
[data-testid="stHeader"] {
    background-color: rgba(13, 17, 23, 0) !important;
    height: 0px !important;
}
h1 {
    margin-top: 0px !important;
    margin-bottom: 15px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.filter-box {
    margin-top: 25px !important;
    margin-bottom: 15px;
}
[data-testid="stVerticalBlock"] > div:has(h3) {
    margin-top: 0px !important;
}
h3 {
    margin-top: 0px !important;
    margin-bottom: 15px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
div[data-testid="metric-container"] {
    background-color: #161b22 !important;
    border: 1px solid #1f6feb !important;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
}
div[data-testid="stMetricLabel"] {
    color: #ffffff !important;
    font-weight: 500;
}
div[data-testid="stMetricValue"] {
    color: #58a6ff !important;
    font-size: 1.6rem !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    font-size: 16px !important;
    padding: 12px 0px !important;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 15px #388bfd;
}
div[data-testid="stSlider"] label {
    color: #ffffff !important;
    font-weight: 500;
}
div[data-testid="stCheckbox"] label p {
    color: #ffffff !important;
    font-weight: 500;
}
div.stAlert p {
    color: #58a6ff !important;
}
h2, h4 {
    color: #ffffff !important;
    font-weight: 600 !important;
}
.earnings-card, .info-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
    height: 100%;
}
.info-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #58a6ff;
    margin-bottom: 8px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 4px;
}
.earnings-label {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
}
.earnings-value {
    font-size: 1.6rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 NASDAQ Scanner Pro")

NASDAQ100_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
    "NFLX", "AMD", "ADBE", "PEP", "CSCO", "TMUS", "QCOM", "AMGN", "INTU", "AMAT",
    "BKNG", "ISRG", "VRTX", "GILD", "LRCX", "MU", "PANW", "KLAC", "MELI", "SNPS",
    "CDNS", "ADI", "MAR", "FTNT", "CRWD", "ORLY", "CSX", "PYPL", "MNST", "AEP",
    "ROP", "ODFL", "DXCM", "KDP", "CTAS", "NXPI", "PCAR", "MRVL", "FAST", "PAYX",
    "TEAM", "DDOG", "ZS", "MDB", "NET", "SHOP", "ROKU", "DOCU", "SNOW",
    "PLTR", "ARM", "SMCI", "WDAY", "BIIB", "REGN", "EXC", "EA", "XEL",
    "IDXX", "FANG", "CPRT", "CHTR", "GEHC", "ON", "TTWO", "CSGP", "BKR", "WBD",
    "VRSK", "MCHP", "MRNA", "ALGN", "LULU", "KHC", "CTSH", "DLTR", "SBUX", "ADSK",
    "TTD", "RIVN", "OKTA", "HUBS", "PDD", "BIDU", "JD", "NTES", "CEG", "GFS"
]

NEW_TICKERS = [
    "JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "AXP", "SCHW", 
    "PNC", "USB", "TFC", "COF", "MET", "PRU", "AFL", "ALL", "CB",
    "JNJ", "UNH", "LLY", "PFE", "MRK", "ABBV", "ABT", "DHR", "BMY", "CVS", 
    "CI", "HCA", "SYK", "BDX", "MDT", "ELV", "GILD", "HUM", "CNC", "ZTS",
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "WMB",
    "LIN", "APD", "ECL", "DD", "FCX", "NEM", "SHW", "IFF", "CTVA", "PPG",
    "PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "CL", "KMB", "GIS",
    "ADM", "MDLZ", "STZ", "HSY", "KR", "SYY", "EL", "CAG", "TSN",
    "UPS", "FDX", "CAT", "DE", "GE", "HON", "BA", "MMM", "LMT", "RTX",
    "GD", "NOC", "GEHC", "ITW", "EMR", "CMI", "CSX", "UNP", "NSC", "JCI",
    "DIS", "NKE", "HD", "LOW", "MCD", "TGT", "TJX", "GM", "F", "BKNG",
    "MAR", "HLT", "EXC", "NEE", "DUK", "SO", "D", "AEP", "SRE", "PEG"
]

TICKERS = list(set(NASDAQ100_TICKERS + NEW_TICKERS))

if "results_df" not in st.session_state:
    st.session_state.results_df = None

if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = None

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_atr(data, period=14):
    high = data['High'].squeeze()
    low = data['Low'].squeeze()
    close = data['Close'].squeeze().shift()
    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

@st.cache_data(ttl=900, show_spinner=False)
def load_all_market_data(tickers, cache_key):
    """
    전체 종목 1년치 일봉을 한 번에 받아 캐싱한다.
    - threads=True: 종목들을 병렬 다운로드 (속도 대폭 향상)
    - cache_key: 'YYYY-MM-DD-(전장후)' 형태. 날짜/장상태가 바뀌면 자동 갱신.
    """
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = yf.download(
        list(tickers),
        start=start_date,
        auto_adjust=True,
        group_by="ticker",
        progress=False,
        threads=True
    )
    return data

@st.cache_data(ttl=3600)
def get_next_earnings_date(ticker):
    """
    다음 실적 발표일을 'YYYY-MM-DD'로 반환. 실패 시 '확인 불가'.
    최신 yfinance에서 calendar는 dict, earnings_dates는 DataFrame이다.
    """
    today = pd.Timestamp(datetime.now().date())

    # 방법 1: t.calendar (dict) — 'Earnings Date' 키에 date 리스트
    try:
        t = yf.Ticker(ticker)
        cal = t.calendar
        if isinstance(cal, dict):
            ed = cal.get("Earnings Date")
            if ed:
                # 리스트이거나 단일 값일 수 있음
                dates = ed if isinstance(ed, (list, tuple)) else [ed]
                parsed = []
                for d in dates:
                    try:
                        parsed.append(pd.Timestamp(d))
                    except Exception:
                        pass
                # 오늘 이후 가장 가까운 날짜 우선, 없으면 가장 최근 값
                future = sorted([d for d in parsed if d >= today])
                if future:
                    return future[0].strftime('%Y-%m-%d')
                if parsed:
                    return sorted(parsed)[-1].strftime('%Y-%m-%d')
        elif isinstance(cal, pd.DataFrame) and not cal.empty:
            # 구버전 호환: DataFrame 형태
            try:
                val = cal.loc["Earnings Date"].iloc[0]
                return pd.Timestamp(val).strftime('%Y-%m-%d')
            except Exception:
                pass
    except Exception:
        pass

    # 방법 2: t.earnings_dates (DataFrame) — 인덱스가 발표일
    try:
        edf = yf.Ticker(ticker).earnings_dates
        if isinstance(edf, pd.DataFrame) and not edf.empty:
            idx = pd.to_datetime(edf.index).tz_localize(None)
            future = sorted([d for d in idx if d >= today])
            if future:
                return future[0].strftime('%Y-%m-%d')
            return sorted(idx)[-1].strftime('%Y-%m-%d')
    except Exception:
        pass

    return "확인 불가"

@st.cache_data(ttl=86400)
def get_company_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        market_cap = info.get("marketCap", 0)
        if market_cap > 0:
            market_cap_str = f"${market_cap / 1e9:,.1f} B"
        else:
            market_cap_str = "N/A"
            
        return {
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "기업 개요 정보가 없습니다."),
            "market_cap": market_cap_str,
            "per": f"{info.get('trailingPE', info.get('forwardPE', 'N/A'))}",
            "pbr": f"{info.get('priceToBook', 'N/A')}"
        }
    except Exception:
        return {
            "sector": "N/A", "industry": "N/A", "summary": "정보를 불러오지 못했습니다.",
            "market_cap": "N/A", "per": "N/A", "pbr": "N/A"
        }

# --- 📊 좌측 컨트롤러(3) : 우측 결과창(7) 분할 ---
left_col, right_col = st.columns([3, 7], gap="large")

with left_col:
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.subheader("⚙️ 조건 필터 설정")
    
    rsi_range = st.slider("RSI 범위 설정 (최소 ~ 최대)", 0, 100, (40, 60))
    rsi_min, rsi_max = rsi_range
    
    exclude_drop_active = st.checkbox("최근 30일 내 20일선 급등락 종목 제외", value=True)
    
    limit_col1, limit_col2 = st.columns(2)
    with limit_col1:
        drop_threshold = st.slider("제외할 하단 이탈률 기준 (%)", 0, 30, 7)
    with limit_col2:
        surge_threshold = st.slider("제외할 상단 돌파율 기준 (%)", 0, 50, 20)
    
    volume_filter_active = st.checkbox("최근 3일 거래대금 스파이크 필터", value=True)
    volume_threshold = st.slider("20일 평균 대비 3일 평균 거래대금 비율 (%)", 100, 300, 120)
    
    chk_col1, chk_col2 = st.columns(2)
    with chk_col1:
        trend_filter_100 = st.checkbox("중기 상승 (현재가 > 100일선)", value=True)
    with chk_col2:
        trend_filter_200 = st.checkbox("대세 상승 (현재가 > 200일선)", value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 조건으로 종목 검색", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if search_clicked:
        results = []

        us_eastern = pytz.timezone('US/Eastern')
        now_us = datetime.now(us_eastern)
        market_open  = now_us.replace(hour=9,  minute=30, second=0, microsecond=0)
        market_close = now_us.replace(hour=16, minute=0,  second=0, microsecond=0)
        weekday = now_us.weekday()
        is_market_open_now = (weekday < 5) and (market_open <= now_us < market_close)

        # ── 기준일 규칙 ──
        # "이미 장 마감이 끝난 가장 최근 거래일"의 종가로 계산한다.
        #   · 평일 16:00 ET 이후       → 오늘 종가 사용 가능
        #   · 평일 장중/장전, 주말/공휴일 → 직전 거래일 종가
        today_us = pd.Timestamp(now_us.strftime('%Y-%m-%d'))
        after_close = (weekday < 5) and (now_us >= market_close)

        with st.spinner("데이터 수집 중..."):
            # 캐시 키: 날짜 + 장 상태(전/중/후). 같은 상태에서 재검색하면 즉시 반환.
            if after_close:
                _phase = "after"
            elif is_market_open_now:
                _phase = "open"
            else:
                _phase = "pre"
            cache_key = f"{now_us.strftime('%Y-%m-%d')}-{_phase}"
            raw = load_all_market_data(tuple(TICKERS), cache_key)

        raw = raw.sort_index()

        # ── 티커별 DataFrame으로 분리 (yfinance 버전·MultiIndex 구조 무관) ──
        ticker_dfs = {}
        if isinstance(raw.columns, pd.MultiIndex):
            names = raw.columns.names
            if names[0] == 'Ticker':
                ticker_level = 0
            elif names[-1] == 'Ticker':
                ticker_level = 1
            else:
                ohlcv = {"Open", "High", "Low", "Close", "Volume", "Adj Close"}
                lv0 = set(raw.columns.get_level_values(0))
                ticker_level = 1 if (lv0 & ohlcv) else 0
            all_tickers_in_raw = list(raw.columns.get_level_values(ticker_level).unique())
            for ticker in TICKERS:
                if ticker in all_tickers_in_raw:
                    df_t = raw.xs(ticker, axis=1, level=ticker_level).copy()
                    for col in ["Open", "High", "Low", "Close", "Volume"]:
                        if col in df_t.columns:
                            df_t[col] = pd.to_numeric(df_t[col], errors="coerce")
                    # 종가가 비어있는 미확정/누락 행 제거
                    df_t = df_t[df_t["Close"].notna()].copy()
                    ticker_dfs[ticker] = df_t
        else:
            df_t = raw.copy()
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col in df_t.columns:
                    df_t[col] = pd.to_numeric(df_t[col], errors="coerce")
            df_t = df_t[df_t["Close"].notna()].copy()
            if TICKERS:
                ticker_dfs[TICKERS[0]] = df_t

        ref_date_str = None  # 화면 표시용 기준일

        for ticker in TICKERS:
            try:
                if ticker not in ticker_dfs:
                    continue

                data = ticker_dfs[ticker]
                if data.empty or len(data) < 200:
                    continue

                # ── 기준 행 선택: 이미 마감된 가장 최근 거래일까지만 사용 ──
                if after_close:
                    usable = data
                else:
                    usable = data[data.index < today_us]
                if len(usable) < 200:
                    continue

                close_series = usable["Close"]
                volume_series = usable["Volume"]

                ma20_series = close_series.rolling(20).mean()
                ma100_series = close_series.rolling(100).mean()
                ma200_series = close_series.rolling(200).mean()
                rsi_series = calculate_rsi(close_series)
                atr_series = calculate_atr(usable)

                # 기준일 = usable의 마지막 행
                price = float(close_series.iloc[-1])
                ma20 = float(ma20_series.iloc[-1])
                ma100 = float(ma100_series.iloc[-1])
                ma200 = float(ma200_series.iloc[-1])
                rsi = float(rsi_series.iloc[-1])
                atr = float(atr_series.iloc[-1])
                stop_price = ma20 - (atr * 1.5)

                if pd.isna(ma20) or pd.isna(rsi) or pd.isna(price) or pd.isna(atr):
                    continue

                # 첫 유효 종목에서 기준일 기록
                if ref_date_str is None:
                    ref_date_str = usable.index[-1].strftime('%Y-%m-%d')

                distance = (price - ma20) / ma20 * 100

                is_match = (price > ma20) and (rsi_min <= rsi <= rsi_max)

                if exclude_drop_active and is_match:
                    recent_close = close_series.iloc[-30:]
                    recent_ma20 = ma20_series.iloc[-30:]
                    recent_distances = (recent_close - recent_ma20) / recent_ma20 * 100
                    recent_distances = recent_distances.dropna()
                    if (recent_distances <= -drop_threshold).any():
                        is_match = False
                    if (recent_distances >= surge_threshold).any():
                        is_match = False

                if volume_filter_active and is_match:
                    value_series = close_series * volume_series
                    # usable은 이미 기준일까지 잘려 있으므로 항상 마지막 포함 계산
                    avg_value_3d = value_series.iloc[-3:].mean()
                    avg_value_20d = value_series.iloc[-20:].mean()

                    if avg_value_20d > 0:
                        ratio = (avg_value_3d / avg_value_20d) * 100
                        if ratio < volume_threshold:
                            is_match = False
                    else:
                        is_match = False

                if trend_filter_100 and price <= ma100:
                    is_match = False
                if trend_filter_200 and price <= ma200:
                    is_match = False

                if is_match:
                    results.append({
                        "종목": ticker,
                        "현재가": round(price, 2),
                        "20일선": round(ma20, 2),
                        "ATR 1.5배 이탈가": round(stop_price, 2),
                        "괴리율(%)": round(distance, 2),
                        "RSI": round(rsi, 2),
                    })
            except Exception:
                pass

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values("괴리율(%)").reset_index(drop=True)
            st.session_state.results_df = df
            st.session_state.selected_ticker = df.iloc[0]["종목"]
        else:
            st.session_state.results_df = pd.DataFrame()
            st.session_state.selected_ticker = None

        # 화면 표시용: 기준 종가일 + 시장 상태 + 조회 시각 저장
        try:
            if ref_date_str:
                _d = pd.Timestamp(ref_date_str)
                wd_kr = ['월', '화', '수', '목', '금', '토', '일'][_d.weekday()]
                st.session_state.ref_date_str = f"{ref_date_str} ({wd_kr})"
            else:
                st.session_state.ref_date_str = None
        except Exception:
            st.session_state.ref_date_str = ref_date_str
        if is_market_open_now:
            st.session_state.market_status = "미국 장중 (직전 거래일 종가 기준)"
        elif after_close:
            st.session_state.market_status = "미국 장 마감 후 (당일 종가 기준)"
        else:
            st.session_state.market_status = "미국 장 시작 전·주말 (최근 거래일 종가 기준)"
        st.session_state.scan_time_kst = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')

    if st.session_state.results_df is not None:
        df = st.session_state.results_df
        st.subheader("📋 스캔된 종목 리스트")

        _ref = st.session_state.get("ref_date_str")
        if _ref:
            _status = st.session_state.get("market_status", "")
            _scan = st.session_state.get("scan_time_kst", "")
            st.markdown(f"""
                <div style="background-color:#161b22; border:1px solid #1f6feb;
                            border-radius:8px; padding:10px 14px; margin-bottom:12px;">
                    <span style="color:#58a6ff; font-weight:600;">📅 기준 종가일: {_ref}</span>
                    <span style="color:#8b949e;">　|　{_status}</span>
                    <span style="color:#6e7681; font-size:12px;">　|　조회: {_scan} KST</span>
                </div>
            """, unsafe_allow_html=True)

        if df.empty:
            st.warning("조건에 맞는 종목이 없습니다.")
        else:
            event = st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=450,
                on_select="rerun",
                selection_mode="single-row",
                key="scanner_table"
            )

            selected_rows = event.get("selection", {}).get("rows", [])
            if selected_rows:
                st.session_state.selected_ticker = df.iloc[selected_rows[0]]["종목"]


# --- 2. 우측 영역 : 상세 지표, 대형 차트 및 기업 정보 추가 ---
with right_col:
    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        df = st.session_state.results_df
        
        if st.session_state.selected_ticker:
            selected_ticker = st.session_state.selected_ticker
            row = df[df["종목"] == selected_ticker].iloc[0]
        else:
            row = df.iloc[0]
            selected_ticker = row["종목"]

        st.markdown(f"### 📊 분석 타겟: <span style='color:#58a6ff; font-size:28px;'>{selected_ticker}</span>", unsafe_allow_html=True)
        st.info("💡 왼쪽 테이블의 행을 클릭하면 실시간으로 우측 종목 정보와 차트가 동기화됩니다.")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("현재가", f"${row['현재가']}")
        c2.metric("20일선", f"${row['20일선']}")
        c3.metric("괴리율", f"{row['괴리율(%)']}%")
        c4.metric("RSI", row["RSI"])
        
        ed_str = get_next_earnings_date(selected_ticker)
        bg_color = "#161b22"
        border_color = "#1f6feb"
        text_color = "#58a6ff"
        ed_display = ed_str  # 화면에 표시할 문자열

        if ed_str not in ("N/A", "확인 불가"):
            try:
                today = datetime.now()
                ed_date = datetime.strptime(ed_str, "%Y-%m-%d")
                days_left = (ed_date - today).days

                # D-day 라벨 추가
                if days_left == 0:
                    ed_display = f"{ed_str} (오늘)"
                elif days_left > 0:
                    ed_display = f"{ed_str} (D-{days_left})"
                else:
                    ed_display = f"{ed_str} (발표완료)"

                if 0 <= days_left <= 7:
                    bg_color = "#2b161a"
                    border_color = "#da3637"
                    text_color = "#ff6b6b"
                elif 7 < days_left <= 30:
                    bg_color = "#262212"
                    border_color = "#d4a373"
                    text_color = "#e5c07b"
            except Exception:
                pass

        with c5:
            st.markdown(f"""
                <div class="earnings-card" style="background-color: {bg_color}; border: 1px solid {border_color};">
                    <div class="earnings-label" style="color: #ffffff;">실적 발표일</div>
                    <div class="earnings-value" style="color: {text_color};">{ed_display}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        chart = yf.download(selected_ticker, period="1y", auto_adjust=True, progress=False)

        if isinstance(chart.columns, pd.MultiIndex):
            # 단일 티커인데 MultiIndex인 경우 (최신 yfinance) → level1에서 ticker 제거
            chart.columns = chart.columns.get_level_values(0)

        # 종가가 비어있는 미확정 행 제거 (마지막 봉이 깨지는 것 방지)
        chart["Close"] = pd.to_numeric(chart["Close"], errors="coerce")
        chart = chart[chart["Close"].notna()]

        chart["MA20"] = chart["Close"].rolling(20).mean()
        chart["MA100"] = chart["Close"].rolling(100).mean()
        chart["MA200"] = chart["Close"].rolling(200).mean()

        fig = go.Figure()
        
        fig.add_trace(
            go.Candlestick(
                x=chart.index, open=chart["Open"], high=chart["High"], low=chart["Low"], close=chart["Close"],
                name="Price", increasing_line_color='#238636', decreasing_line_color='#da3637'
            )
        )

        fig.add_trace(go.Scatter(x=chart.index, y=chart["MA20"], name="20 MA", line=dict(color='#58a6ff', width=1.5)))
        fig.add_trace(go.Scatter(x=chart.index, y=chart["MA100"], name="100 MA", line=dict(color='#a371f7', width=1.5, dash='dot')))
        fig.add_trace(go.Scatter(x=chart.index, y=chart["MA200"], name="200 MA", line=dict(color='#ff9922', width=2, dash='dash')))

        fig.update_layout(
            template="plotly_dark", paper_bgcolor='#0d1117', plot_bgcolor='#161b22', height=500, 
            xaxis_rangeslider_visible=False, title=f"{selected_ticker} 1-Year Technical Chart",
            margin=dict(l=30, r=60, t=50, b=30), dragmode='pan',
            hovermode='x unified',
            legend=dict(
                yanchor="bottom",
                y=0.02,
                xanchor="right",
                x=0.98,
                bgcolor="rgba(22, 27, 34, 0.8)",
                bordercolor="#30363d",
                borderwidth=1
            ),
            yaxis=dict(
                side="right",
                showgrid=True,
                gridcolor="#21262d",
                tickformat="$.2f"
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="#21262d"
            )
        )

        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        
        st.markdown("<br>", unsafe_allow_html=True)
        comp_info = get_company_info(selected_ticker)
        
        info_col1, info_col2 = st.columns([6, 4], gap="medium")
        
        with info_col1:
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">🏢 기업 개요 Profile</div>
                    <p style="margin: 4px 0;"><b>섹터:</b> {comp_info['sector']}</p>
                    <p style="margin: 4px 0;"><b>산업군:</b> {comp_info['industry']}</p>
                    <p style="margin: 10px 0 0 0; color: #8b949e; font-size: 13.5px; line-height: 1.5; text-align: justify;">
                        {comp_info['summary']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        with info_col2:
            try:
                per_val = f"{float(comp_info['per']):.2f}" if comp_info['per'] != "N/A" else "N/A"
                pbr_val = f"{float(comp_info['pbr']):.2f}" if comp_info['pbr'] != "N/A" else "N/A"
            except ValueError:
                per_val = comp_info['per']
                pbr_val = comp_info['pbr']
                
            st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">📊 핵심 펀더멘탈 지표</div>
                    <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
                        <tr style="border-bottom: 1px solid #21262d;">
                            <td style="padding: 10px 0; color: #8b949e;">시가총액 (Market Cap)</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #ffffff;">{comp_info['market_cap']}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #21262d;">
                            <td style="padding: 10px 0; color: #8b949e;">PER (주가수익비율)</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #ff9922;">{per_val} 배</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; color: #8b949e;">PBR (주가순자산비율)</td>
                            <td style="padding: 10px 0; text-align: right; font-weight: bold; color: #a371f7;">{pbr_val} 배</td>
                        </tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
    elif st.session_state.results_df is not None and st.session_state.results_df.empty:
        with right_col:
            st.info("좌측에서 조건을 설정한 후 검색 버튼을 눌러주세요.")
            