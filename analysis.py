import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()

        # Calculation of Price Movement (Returns)
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).replace([np.inf, -np.inf], 0).fillna(0)
        
        # Amihud Measure: Lower = Institutional Absorption | Higher = Retail Volatility
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # Relative Volume (Compared to market average)
        df['rvol'] = df['volume'] / (df['volume'].median() + 1e-9)

        # ML Cluster Detection
        try:
            X = df[['volume', 'turnover', 'amihud']].fillna(0)
            X_norm = (X - X.mean()) / (X.std() + 1e-9)
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(X_norm)
            
            # Identify the cluster with the highest median turnover
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = df['cluster'] == inst_id
        except:
            df['is_institutional'] = False

        return df
        
