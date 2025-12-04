import streamlit as st
import requests
import pandas as pd
import random
import time
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. 页面配置 & 黑金 CSS 样式注入
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sentiment-X",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 强制注入 CSS 以还原“赛博黑金”风格
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: #020617;
        color: #e2e8f0;
    }
    /* 标题样式 */
    h1 {
        color: #facc15 !important;
        font-family: 'Courier New', monospace;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: -2px;
    }
    /* Metric 卡片样式 */
    div[data-testid="stMetric"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(234, 179, 8, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc;
        font-family: monospace;
    }
    /* 情绪数值颜色动态化 */
    .sentiment-greed { color: #4ade80; }
    .sentiment-fear { color: #f87171; }
    
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 数据获取函数 (API)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=60) # 缓存60秒，防止刷新太快被封IP
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # 失败时的兜底数据
        return {
            "bitcoin": {"usd": 96450.20, "usd_24h_change": 2.45},
            "ethereum": {"usd": 3450.12, "usd_24h_change": -1.20}
        }

@st.cache_data(ttl=3600) # 情绪指数一天才变一次，缓存久一点
def get_sentiment():
    try:
        url = "https://api.alternative.me/fng/?limit=7"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data['data']
    except:
        # 兜底数据
        return [{"value": "78", "value_classification": "Extreme Greed", "timestamp": str(int(time.time()))}] * 7

# -----------------------------------------------------------------------------
# 3. 模拟新闻生成器
# -----------------------------------------------------------------------------
def get_news():
    headlines = [
        ("BlackRock 比特币 ETF 交易量突破历史新高", "positive"),
        ("美联储暗示将在下个季度维持利率不变", "neutral"),
        ("某巨鲸刚刚向交易所转入 10,000 ETH", "negative"),
        ("SEC 推迟了关于以太坊现货 ETF 的决议", "negative"),
        ("MicroStrategy 再次购入 500 BTC", "positive"),
        ("通胀数据略高于预期，市场出现恐慌情绪", "negative"),
    ]
    # 随机返回3条
    return random.sample(headlines, 3)

# -----------------------------------------------------------------------------
# 4. 主页面布局
# -----------------------------------------------------------------------------

# 标题
st.title("SENTIMENT-X")
st.caption("Market Compass | Powered by Streamlit")

# 获取数据
prices = get_crypto_prices()
sentiment_data = get_sentiment()
current_sentiment = sentiment_data[0]
history = pd.DataFrame(sentiment_data)
history['timestamp'] = pd.to_datetime(history['timestamp'], unit='s')
history['value'] = history['value'].astype(int)

# --- 第一部分：情绪仪表盘 ---
st.markdown("### 📡 Market Sentiment")

col1, col2 = st.columns([1, 2])

with col1:
    # 情绪数值
    val = int(current_sentiment['value'])
    delta_color = "normal"
    if val > 75: delta_color = "inverse" # 贪婪是反向风险
    
    st.metric(
        label="Fear & Greed Index",
        value=val,
        delta=current_sentiment['value_classification'],
        delta_color="off"
    )

with col2:
    # 简单的趋势图
    chart_data = history.sort_values('timestamp').set_index('timestamp')['value']
    st.area_chart(chart_data, color="#eab308", height=120)

# --- 第二部分：资产看板 ---
st.markdown("### 🛡️ Asset Watchlist")
c1, c2 = st.columns(2)

with c1:
    btc = prices['bitcoin']
    st.metric(
        label="Bitcoin (BTC)",
        value=f"${btc['usd']:,.0f}",
        delta=f"{btc['usd_24h_change']:.2f}%"
    )

with c2:
    eth = prices['ethereum']
    st.metric(
        label="Ethereum (ETH)",
        value=f"${eth['usd']:,.0f}",
        delta=f"{eth['usd_24h_change']:.2f}%"
    )

# --- 第三部分：实时快讯 ---
st.markdown("### 📰 Live Feed")
news_items = get_news()

for text, sentiment in news_items:
    color = "green" if sentiment == "positive" else "red" if sentiment == "negative" else "grey"
    st.markdown(f"""
    <div style='background-color: #1e293b; padding: 10px; border-radius: 5px; margin-bottom: 8px; border-left: 3px solid {color};'>
        <div style='color: #cbd5e1; font-size: 14px;'>{text}</div>
        <div style='color: {color}; font-size: 10px; text-transform: uppercase; margin-top: 4px;'>{sentiment}</div>
    </div>
    """, unsafe_allow_html=True)

# 底部
st.divider()
st.markdown("<div style='text-align: center; color: #475569; font-size: 12px;'>SENTIMENT-X PYTHON BUILD v1.0</div>", unsafe_allow_html=True)
