import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Institutional", layout="wide")

# Initialization
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = NepseFetcher()
if 'engine' not in st.session_state:
    st.session_state.engine = InstitutionalEngine()

st.title("🛡️ Institutional Intelligence System (NEPSE)")

try:
    # 1. Fetch & Analyze
    raw_data = st.session_state.fetcher.get_live_data()
    data = st.session_state.engine.apply_metrics(raw_data)
    avg_amihud = data['amihud'].median()

    # 2. Logic to prevent NameError
    summary_list = []
    for _, row in data.iterrows():
        res = SignalLab.get_summary(row, avg_amihud)
        if res['Signal'] != "NEUTRAL":
            summary_list.append(res)

    # 3. UI
    tab1, tab2 = st.tabs(["🎯 AI Trade Signals", "📋 Microstructure Data"])

    with tab1:
        if summary_list:
            summary_df = pd.DataFrame(summary_list)
            st.success(f"Found {len(summary_df)} Institutional Setups")
            st.dataframe(summary_df[['Symbol', 'Signal', 'SimpleSummary', 'Target', 'StopLoss']], use_container_width=True)
        else:
            st.info("No high-conviction institutional patterns detected in current data.")

    with tab2:
        st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error(f"Critical Runtime Error: {e}")
    st.info("Market may be closed or site structure has changed. Using fallback data.")
    
