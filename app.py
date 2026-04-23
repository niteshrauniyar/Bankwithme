import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine

# 1. Page Configuration
st.set_page_config(page_title="NEPSE Institutional Intelligence", layout="wide")

# 2. Initialization
fetcher = NepseFetcher()
engine = InstitutionalEngine()

st.title("🏛️ NEPSE Institutional Intelligence")
st.subheader("Smart Money & Liquidity Detection Engine")

# 3. Data Pipeline with Caching
@st.cache_data(ttl=300) # Refresh data every 5 minutes
def load_and_analyze():
    raw_df = fetcher.get_live_data()
    if raw_df is None or raw_df.empty:
        return None
    processed_df = engine.apply_metrics(raw_df)
    return processed_df

# 4. Execution
data = load_and_analyze()

if data is not None:
    # Sidebar Filters
    st.sidebar.header("Scan Filters")
    min_vol = st.sidebar.slider("Min Volume", 0, int(data['volume'].max()), 1000)
    filtered_data = data[data['volume'] >= min_vol]

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Market Symbols", len(data))
    m2.metric("Institutional Activity", f"{len(data[data['is_institutional']])} Symbols")
    m3.metric("Avg Market Volatility", f"{data['returns'].mean()*100:.2f}%")

    tab1, tab2, tab3 = st.tabs(["🎯 High Conviction Signals", "🧠 Institutional Footprint", "📋 All Data"])

    with tab1:
        # Signal Logic: High Volume + Low Price Impact (Absorption)
        signals = data[(data['is_institutional']) & (data['ltp'] > data['open'])].copy()
        if not signals.empty:
            st.success("Strong Institutional Accumulation Detected in these symbols:")
            st.dataframe(signals[['symbol', 'ltp', 'volume', 'amihud']], use_container_width=True)
        else:
            st.info("No high-conviction institutional signals at this moment.")

    with tab2:
        fig = px.scatter(data, x="volume", y="amihud", color="is_institutional",
                         hover_name="symbol", size="turnover", log_x=True,
                         title="Price Impact (Amihud) vs Volume Cluster",
                         template="plotly_dark", color_discrete_map={True: '#00ff00', False: '#444444'})
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.dataframe(data.sort_values(by='turnover', ascending=False), use_container_width=True)
else:
    st.error("Could not fetch data from NEPSE sources. Please check connection.")
    
