import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Official Pro", layout="wide")

st.title("🏛️ NEPSE Official Intelligence Terminal")
st.markdown("Fetching data directly from **nepalstock.com.np**")

fetcher = NepseFetcher()
engine = InstitutionalEngine()

# Data Logic
data = fetcher.get_live_data()
data = engine.apply_metrics(data)

if not data.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Symbols", len(data))
    m2.metric("Mkt Volatility", f"{data['returns'].mean()*100:.2f}%")
    m3.metric("Inst. Active", len(data[data['is_institutional']]))

    tab1, tab2 = st.tabs(["🎯 Trade Signals", "🔍 Full Market Depth"])

    with tab1:
        mkt_amihud = data['amihud'].median()
        summaries = [SignalLab.get_summary(row, mkt_amihud) for _, row in data.iterrows()]
        res_df = pd.DataFrame(summaries)
        
        # Show actionable items
        action_df = res_df[res_df['Verdict'] != "WAIT"].sort_values('Confidence', ascending=False)
        if not action_df.empty:
            st.dataframe(action_df, use_container_width=True, hide_index=True)
        else:
            st.info("No significant institutional footprints detected in this session.")

    with tab2:
        st.dataframe(data.sort_values('turnover', ascending=False), use_container_width=True)

    if st.button("🔄 Force Refresh"):
        st.rerun()
else:
    st.error("⚠️ Error: Official NEPSE site is not returning data. Check market hours (Sun-Thu, 11AM-3PM).")
    
