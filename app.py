import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Institutional Pro", layout="wide")

st.title("🏹 NEPSE Institutional Terminal")
st.caption("Live Market Microstructure & ML-Based Accumulation Detector")

# Persistent State
if 'data' not in st.session_state:
    with st.spinner("Fetching Market Depth..."):
        raw = NepseFetcher().get_live_data()
        st.session_state.data = InstitutionalEngine().apply_metrics(raw)

data = st.session_state.data

if not data.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Active Symbols", len(data))
    m2.metric("Market Volatility", f"{data['returns'].mean()*100:.2f}%")
    m3.metric("Inst. Liquidity", f"{len(data[data['is_institutional']])} Stocks")

    tab1, tab2 = st.tabs(["🎯 Smart Money Signals", "📋 Raw Quant Matrix"])

    with tab1:
        mkt_amihud = data['amihud'].median()
        summaries = [SignalLab.get_summary(row, mkt_amihud) for _, row in data.iterrows()]
        res_df = pd.DataFrame(summaries)
        
        # Show only signals worth acting on
        trade_df = res_df[res_df['Action'] != "WAIT"].sort_values('Confidence', ascending=False)
        if not trade_df.empty:
            st.dataframe(trade_df, use_container_width=True, hide_index=True)
        else:
            st.info("Market is currently quiet. No institutional breakouts detected.")

    with tab2:
        st.dataframe(data.sort_values('turnover', ascending=False), use_container_width=True)

    if st.button("🔄 Refresh Data"):
        st.session_state.clear()
        st.rerun()
else:
    st.error("Critical: Could not fetch market data or fallback.")
    
