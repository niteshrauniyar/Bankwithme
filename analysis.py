import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        if df.empty: return df
        df = df.copy()
        
        # Microstructure Math
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        df['v_strength'] = df['volume'] / (df['volume'].median() + 1e-9)
        
        try:
            # Cluster to find big players
            X = df[['volume', 'turnover']].fillna(0)
            X_norm = (X - X.mean()) / (X.std() + 1e-9)
            kmeans = KMeans(n_clusters=min(len(df), 3), n_init=10, random_state=42)
            df['cluster'] = kmeans.fit_predict(X_norm)
            inst_id = df.groupby('cluster')['turnover'].median().idxmax()
            df['is_institutional'] = (df['cluster'] == inst_id)
        except:
            df['is_institutional'] = False
        return df
        
