class SignalLab:
    @staticmethod
    def compute(df):
        results = []
        for _, row in df.iterrows():
            score = 0
            reasons = []
            
            # Smart Money Accumulation Check
            if row['is_institutional'] and row['ltp'] > row['open']:
                score += 50
                reasons.append("Institutional Accumulation")
            
            # Liquidity Trap Check
            if row['amihud'] < df['amihud'].quantile(0.2):
                score += 20
                reasons.append("Deep Liquidity (Lower Impact)")

            # Momentum / RVOL
            if row['rvol'] > 2.0:
                score += 15
                reasons.append("Extreme Volume Spike")

            # Final Verdict
            verdict = "HOLD"
            if score >= 65: verdict = "STRONG BUY"
            elif score >= 40: verdict = "BUY"
            elif row['change_pct'] < -3 and row['is_institutional']: verdict = "INSTITUTIONAL DUMP"

            # Institutional Levels (Volume Profile Logic)
            entry = row['ltp']
            # Support/Resistance based on 2% volatility buffer for NEPSE
            sl = entry * 0.955
            tp1 = entry * 1.07
            tp2 = entry * 1.15
            
            results.append({
                'Symbol': row['symbol'],
                'Signal': verdict,
                'Confidence': score,
                'Reasoning': " + ".join(reasons) if reasons else "Market Noise",
                'Entry': f"{entry:.2f}",
                'StopLoss': f"{sl:.2f}",
                'Target': f"{tp1:.2f}"
            })
        return pd.DataFrame(results)
      
