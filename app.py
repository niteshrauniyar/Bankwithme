import streamlit as st
import pandas as pd
import plotly.express as px
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Institutional Intelligence", layout="wide")

# Custom CSS for Institutional "Terminal" look
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# Persistence & Data Loading
fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("🏛️ NEPSE Institutional Intelligence")
st.caption("Live Order-Flow & Smart Money Detection Engine")

@st.cache_data(ttl=60) # Cache for 1 minute to avoid getting IP banned
def get_processed_data():
    raw = fetcher.get_live_data()
    analyzed = engine.apply_metrics(raw)
    signals = SignalLab.compute(analyzed)
    return analyzed, signals

try:
    data, signals = get_processed_data()

    # Dashboard Top Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Sentiment", "BULLISH" if data['change_pct'].mean() > 0 else "BEARISH")
    c2.metric("Avg. Volatility", f"{data['returns'].mean()*100:.2f}%")
    c3.metric("Institutional Stocks", len(data[data['is_institutional']]))
    c4.metric("Active Symbols", len(data))

    tab1, tab2, tab3 = st.tabs(["🎯 Trade Signals", "🧠 Institutional Analysis", "📈 Market Scan"])

    with tab1:
        # Show only high confidence signals
        high_conviction = signals[signals['Confidence'] > 40].sort_values('Confidence', ascending=False)
        st.dataframe(high_conviction, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Smart Money Footprint (Volume vs Price Impact)")
        fig = px.scatter(data, x="volume", y="amihud", color="is_institutional", 
                         size="turnover", hover_name="symbol",
                         log_x=True, template="plotly_dark",
                         title="Red dots indicate Institutional Clustering")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Full Market Heatmap")
        st.dataframe(data[['symbol', 'ltp', 'change_pct', 'volume', 'is_institutional']], use_container_width=True)

except Exception as e:
    st.error(f"System Error: {e}")
    st.info("Check internet connection or NEPSE server status.")

st.sidebar.markdown("---")
st.sidebar.write("⚡ **Data Source:** ShareSansar/NEPSE Alpha")
st.sidebar.write("🤖 **Model:** Quantitative Microstructure v2.1")
