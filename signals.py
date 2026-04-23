import pandas as pd

class SignalLab:
    @staticmethod
    def get_summary(row, df_avg_amihud):
        score = 0
        verdict = "NEUTRAL"
        reasons = []

        # Research Logic: Institutional Accumulation (Price Up + Inst Cluster)
        if row['is_institutional'] and row['ltp'] > row['open']:
            score += 40
            reasons.append("Institutional Accumulation (Cluster Detected)")
        
        # Research Logic: Low Price Impact (Amihud < Median)
        # Signifies 'Informed Trading' absorbing supply without moving price too much
        if row['amihud'] < df_avg_amihud:
            score += 25
            reasons.append("Efficient Absorption (Low Market Impact)")

        # Research Logic: Volume Strength (Metaorder Signature)
        if row['v_strength'] > 2.0:
            score += 20
            reasons.append("Order Splitting Signature (High Relative Volume)")

        # Final Verdict Calculation
        if score >= 60: verdict = "STRONG BUY"
        elif score >= 40: verdict = "BUY"
        elif row['ltp'] < row['open'] and row['is_institutional']: verdict = "INSTITUTIONAL DISTRIBUTION (SELL)"

        # Target Calculation based on Volatility + 2026 NEPSE Ranges
        entry = row['ltp']
        target = entry * 1.12 if verdict == "STRONG BUY" else entry * 1.07
        sl = entry * 0.94

        return {
            'Symbol': row['symbol'],
            'Signal': verdict,
            'Target': round(target, 1),
            'StopLoss': round(sl, 1),
            'Insight': " | ".join(reasons) if reasons else "Retail Noise"
        }
        
