import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # --- 1. Advanced Liquidity & Impact Metrics ---
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        # Amihud (Price impact per 1M NPR)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        # Kyle's Lambda (Volatility per unit of Volume)
        df['kyle_lambda'] = df['returns'] / (np.sqrt(df['volume']) + 1e-9)

        # --- 2. Market Microstructure & Volatility ---
        # High Volatility Regime Check
        df['volatility_regime'] = np.where(df['returns'] > df['returns'].mean() + df['returns'].std(), "HIGH", "NORMAL")
        
        # Relative Volume (RVOL) - Current vol vs Market median
        df['rvol'] = df['volume'] / (df['volume'].median() + 1e-9)

        # --- 3. Institutional Presence (ML Clustering) ---
        try:
            # We look for "Outliers" in Turnover and Kyle's Lambda
            features = df[['volume', 'turnover', 'kyle_lambda']].fillna(0)
            # Z-Score Normalization
            features_norm = (features - features.mean()) / (features.std() + 1e-9)
            
            kmeans = KMeans(n_clusters=min(len(df), 4), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(features_norm)
            
            # Label the cluster with the highest median turnover as 'Smart Money'
            inst_cluster = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_cluster
        except:
            df['is_institutional'] = False

        return df
        
