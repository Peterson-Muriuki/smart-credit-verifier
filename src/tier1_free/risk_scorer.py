"""
Tier 1: Free Risk Scoring
Uses free signals to score creditworthiness
"""

import pandas as pd
import numpy as np

class Tier1RiskScorer:
    """
    Score applications using only free data
    Cost: KES 0
    """
    
    def score_application(self, application):
        """
        Generate risk score from free signals
        Returns score 0-100 (higher = better)
        """
        
        score = 50  # Start neutral
        positive_signals = []
        negative_signals = []
        
        # SIM age (strong signal)
        if application['sim_age_months'] >= 24:
            score += 15
            positive_signals.append(f"Established SIM ({application['sim_age_months']:.0f} months)")
        elif application['sim_age_months'] >= 12:
            score += 8
            positive_signals.append("Moderate SIM age")
        elif application['sim_age_months'] < 3:
            score -= 15
            negative_signals.append("Very new SIM")
        
        # Device age
        if application['device_age_months'] >= 12:
            score += 8
            positive_signals.append("Established device")
        
        # Device value (higher value = more stable)
        if application['device_value_ksh'] >= 40000:
            score += 10
            positive_signals.append(f"High-value device (KES {application['device_value_ksh']:,})")
        elif application['device_value_ksh'] >= 15000:
            score += 5
            positive_signals.append("Mid-range device")
        
        # Postpaid line (passed telco credit check)
        if application['line_type'] == 'postpaid':
            score += 12
            positive_signals.append("Postpaid line (telco-verified)")
        
        # Application behavior
        completion_time = application['completion_time_seconds']
        if 300 <= completion_time <= 900:  # 5-15 minutes
            score += 5
            positive_signals.append("Normal completion time")
        elif completion_time < 120:
            score -= 10
            negative_signals.append("Suspiciously fast")
        
        # Application hour
        hour = application['application_hour']
        if 9 <= hour <= 21:
            score += 3
            positive_signals.append("Normal business hours")
        else:
            score -= 5
            negative_signals.append(f"Odd hours ({hour}:00)")
        
        # Copy-paste behavior
        if application['copy_paste_count'] == 0:
            score += 3
            positive_signals.append("No copy-paste (organic)")
        elif application['copy_paste_count'] > 5:
            score -= 8
            negative_signals.append("Excessive copy-paste")
        
        # Location verification
        if application['gps_matches_address']:
            score += 5
            positive_signals.append("GPS verified")
        else:
            score -= 10
            negative_signals.append("Location mismatch")
        
        # Velocity check
        if application['applications_last_24h'] == 1:
            score += 5
            positive_signals.append("Single application")
        else:
            score -= application['applications_last_24h'] * 5
            negative_signals.append(f"{application['applications_last_24h']} apps in 24h")
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Tier classification
        if score >= 75:
            tier = 'EXCELLENT'
            recommendation = 'AUTO_APPROVE'
        elif score >= 60:
            tier = 'GOOD'
            recommendation = 'PROCEED_TO_TIER2'
        elif score >= 40:
            tier = 'FAIR'
            recommendation = 'PROCEED_TO_TIER2'
        else:
            tier = 'POOR'
            recommendation = 'AUTO_REJECT'
        
        return {
            'tier1_score': score,
            'tier': tier,
            'recommendation': recommendation,
            'positive_signals': positive_signals,
            'negative_signals': negative_signals,
            'cost': 0
        }
    
    def batch_score(self, df):
        """Score multiple applications"""
        results = []
        for _, row in df.iterrows():
            result = self.score_application(row)
            result['application_id'] = row['application_id']
            results.append(result)
        return pd.DataFrame(results)

if __name__ == "__main__":
    df = pd.read_csv('data/raw/loan_applications.csv')
    scorer = Tier1RiskScorer()
    results = scorer.batch_score(df)
    
    print("Tier 1 Risk Scoring Results:")
    print(results['recommendation'].value_counts())
    print(f"\nAverage Score: {results['tier1_score'].mean():.1f}")
    print(f"Total Cost: KES 0 (FREE)")