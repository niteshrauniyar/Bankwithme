import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Hard-Quant", layout="wide")

st.title("🏛️ NEPSE Institutional Terminal")

fetcher = NepseFetcher()
engine = InstitutionalEngine()

if st.button("🚀 Fetch Hard Data"):
    raw = fetcher.get_live_data()
    if not raw.empty:
        data = engine.apply_metrics(raw)
        
        # Generate Signals
        signals = [SignalLab.get_advice(row) for _, row in data.iterrows()]
        sig_df = pd.DataFrame(signals)
        
        t1, t2 = st.tabs(["🎯 Trade Signals", "📊 Market Scanner"])
        
        with t1:
            # Filter only for Buy/Sell
            actionable = sig_df[sig_df['Action'] != "WAIT"].sort_values('Confidence', ascending=False)
            if not actionable.empty:
                st.dataframe(actionable, use_container_width=True, hide_index=True)
            else:
                st.info("No institutional signals found. Market is currently retail-driven.")
                
        with t2:
            st.dataframe(data, use_container_width=True)
    else:
        st.error("Failed to fetch data. Market might be closed or API is restricted.")
        
