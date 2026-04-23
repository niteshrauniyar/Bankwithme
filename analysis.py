import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class InstitutionalEngine:
    @staticmethod
    def apply_metrics(df):
        # Ensure we have data to work with
        if df.empty: return df

        # Calculate Returns safely
        df['returns'] = (abs(df['ltp'] - df['open']) / df['open']).fillna(0)
        
        # Amihud Illiquidity (Price Impact per Million NPR)
        # We add 1 to denominator to avoid DivideByZero if turnover is 0
        df['amihud'] = df['returns'] / ((df['turnover'] / 1_000_000) + 1e-9)
        
        # Institutional Clustering
        try:
            if len(df) >= 3:
                # Use Volume and Turnover as indicators of Big Money
                features = df[['volume', 'turnover']].fillna(0)
                # Scale features for KMeans
                features_norm = (features - features.mean()) / features.std()
                
                kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
                df['cluster'] = kmeans.fit_predict(features_norm.fillna(0))
                
                # Tag the cluster with the highest median turnover as 'Institutional'
                inst_cluster = df.groupby('cluster')['turnover'].median().idxmax()
                df['is_institutional'] = df['cluster'] == inst_cluster
            else:
                df['is_institutional'] = False
        except:
            df['is_institutional'] = False

        # Relative Volume
        df['rvol'] = df['volume'] / (df['volume'].median() + 1)
        df['change_pct'] = ((df['ltp'] - df['open']) / df['open']) * 100
        
        return df
        
