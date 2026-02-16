"""
Tier 1: Free Fraud Detection
No external API costs
"""

import pandas as pd
import numpy as np

class Tier1FraudDetector:
    """
    Detect obvious fraud using free signals
    Cost: KES 0 per check
    """
    
    def __init__(self):
        self.fraud_rules = {
            'brand_new_sim': {'threshold': 1, 'weight': 0.30},
            'velocity_attack': {'threshold': 2, 'weight': 0.40},
            'rushed_application': {'threshold': 120, 'weight': 0.15},
            'night_application': {'threshold': (22, 6), 'weight': 0.10},
            'excessive_copy_paste': {'threshold': 5, 'weight': 0.15},
            'location_mismatch': {'threshold': 0, 'weight': 0.20}
        }
    
    def detect_fraud(self, application):
        """
        Check for fraud signals
        Returns: fraud_score (0-100), signals, verdict
        """
        
        fraud_score = 0
        fraud_signals = []
        
        # Check 1: Brand new SIM (fraudsters use new SIMs)
        if application['sim_age_months'] < self.fraud_rules['brand_new_sim']['threshold']:
            fraud_score += self.fraud_rules['brand_new_sim']['weight'] * 100
            fraud_signals.append('Brand new SIM card (< 1 month old)')
        
        # Check 2: Velocity attack (multiple applications)
        if application['applications_last_24h'] > self.fraud_rules['velocity_attack']['threshold']:
            fraud_score += self.fraud_rules['velocity_attack']['weight'] * 100
            fraud_signals.append(f"Multiple applications: {application['applications_last_24h']} in 24h")
        
        # Check 3: Rushed application (bots/prepared fraud)
        if application['completion_time_seconds'] < self.fraud_rules['rushed_application']['threshold']:
            fraud_score += self.fraud_rules['rushed_application']['weight'] * 100
            fraud_signals.append(f"Suspiciously fast: {application['completion_time_seconds']}s")
        
        # Check 4: Odd hours (fraudsters work at night)
        hour = application['application_hour']
        if hour >= 22 or hour <= 6:
            fraud_score += self.fraud_rules['night_application']['weight'] * 100
            fraud_signals.append(f"Late night application: {hour}:00")
        
        # Check 5: Excessive copy-paste (prepared data)
        if application['copy_paste_count'] > self.fraud_rules['excessive_copy_paste']['threshold']:
            fraud_score += self.fraud_rules['excessive_copy_paste']['weight'] * 100
            fraud_signals.append(f"Excessive copy-paste: {application['copy_paste_count']} times")
        
        # Check 6: GPS doesn't match address
        if not application['gps_matches_address']:
            fraud_score += self.fraud_rules['location_mismatch']['weight'] * 100
            fraud_signals.append("GPS location doesn't match declared address")
        
        # Verdict
        if fraud_score >= 50:
            verdict = 'REJECT_FRAUD'
        elif fraud_score >= 30:
            verdict = 'HIGH_RISK'
        else:
            verdict = 'PASS'
        
        return {
            'fraud_score': min(fraud_score, 100),
            'fraud_signals': fraud_signals,
            'verdict': verdict,
            'cost': 0  # FREE
        }
    
    def batch_detect(self, df):
        """Process multiple applications"""
        results = []
        for _, row in df.iterrows():
            result = self.detect_fraud(row)
            result['application_id'] = row['application_id']
            results.append(result)
        return pd.DataFrame(results)

if __name__ == "__main__":
    # Test
    df = pd.read_csv('data/raw/loan_applications.csv')
    detector = Tier1FraudDetector()
    results = detector.batch_detect(df)
    
    print("Tier 1 Fraud Detection Results:")
    print(results['verdict'].value_counts())
    print(f"\nTotal Cost: KES 0 (FREE)")