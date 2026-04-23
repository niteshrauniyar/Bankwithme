import streamlit as st
import pandas as pd
from data_fetcher import NepseFetcher
from analysis import InstitutionalEngine
from signals import SignalLab

st.set_page_config(page_title="NEPSE Institutional Pro", layout="wide")

# Persistent Data Loading
@st.cache_data(ttl=60)
def get_market_data():
    raw = NepseFetcher().get_live_data()
    processed = InstitutionalEngine().apply_metrics(raw)
    return processed

st.title("🏛️ NEPSE Advanced Quant Terminal")

try:
    data = get_market_data()
    
    # Global Stats for Signal Logic
    stats = {
        'amihud_median': data['amihud'].median(),
        'vol_median': data['volume'].median()
    }

    # Dashboard Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Symbols", len(data))
    m2.metric("Institutional Stocks", len(data[data['is_institutional']]))
    m3.metric("Avg Mkt Volatility", f"{data['returns'].mean()*100:.2f}%")
    m4.metric("Active Metaorders", len(data[data['rvol'] > 3]))

    tab1, tab2, tab3 = st.tabs(["🎯 AI Signals", "🔍 Institutional Matrix", "📈 Full Market Scanner"])

    with tab1:
        signals = []
        for _, row in data.iterrows():
            sig = SignalLab.get_summary(row, stats)
            if sig['Signal'] != "WAIT":
                signals.append(sig)
        
        if signals:
            sig_df = pd.DataFrame(signals).sort_values(by='Confidence', ascending=False)
            st.dataframe(sig_df[['Symbol', 'Signal', 'Confidence', 'Target', 'SimpleSummary']], use_container_width=True, hide_index=True)
        else:
            st.info("Market is currently quiet. No institutional footprints detected.")

    with tab2:
        st.subheader("Smart Money Cluster Analysis")
        inst_only = data[data['is_institutional']].sort_values(by='turnover', ascending=False)
        st.dataframe(inst_only[['symbol', 'ltp', 'volume', 'amihud', 'kyle_lambda', 'volatility_regime']], use_container_width=True)

    with tab3:
        st.subheader("All Sector Data")
        st.dataframe(data, use_container_width=True)

except Exception as e:
    st.error(f"Engine Error: {e}")
    
