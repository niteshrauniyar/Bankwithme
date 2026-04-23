import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # --- 1. Institutional Footprint (Amihud & Kyle) ---
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).replace([np.inf, -np.inf], 0).fillna(0)
        # Amihud: Higher value means "Price is being pushed by small trades" (Retail)
        # Lower value with high volume means "Large trades are being absorbed" (Institutional)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # --- 2. Order Flow Strength (RVOL) ---
        # Relative Volume compares current stock volume to the market average
        df['rvol'] = df['volume'] / (df['volume'].median() + 1e-9)

        # --- 3. ML Institutional Clustering ---
        try:
            # We use Volume, Turnover, and Amihud to find the "Smart Money" cluster
            features = df[['volume', 'turnover', 'amihud']].fillna(0)
            features_norm = (features - features.mean()) / (features.std() + 1e-9)
            
            kmeans = KMeans(n_clusters=min(len(df), 4), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(features_norm)
            
            # The cluster with the highest turnover/volume ratio is Institutional
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_id
        except:
            df['is_institutional'] = False

        # --- 4. Volatility Regime ---
        df['vol_status'] = np.where(df['returns'] > df['returns'].quantile(0.75), "🔥 High Vol", "🛡️ Stable")
        
        return df
        
