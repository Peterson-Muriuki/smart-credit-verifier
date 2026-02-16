"""
Tier 2: Cheap Verification APIs
Simulates IPRS, KRA, NSSF checks
Cost: KES 10-20 per check
"""

import pandas as pd
import numpy as np
import random

class Tier2Verifier:
    """
    Cheap verification checks
    Cost: KES 10-20 per application
    """
    
    def __init__(self):
        self.cost_per_check = {
            'iprs': 10,
            'kra': 5,
            'nssf': 5
        }
    
    def verify_identity(self, application):
        """
        IPRS Identity Verification
        Cost: KES 10
        Verifies ID is valid and matches name
        """
        
        # Simulate IPRS check
        iprs_verified = application['iprs_verified']
        
        return {
            'check': 'IPRS',
            'verified': bool(iprs_verified),
            'confidence': 0.95 if iprs_verified else 0.0,
            'cost': self.cost_per_check['iprs']
        }
    
    def verify_kra(self, application):
        """
        KRA PIN Verification
        Cost: KES 5
        Verifies tax compliance
        """
        
        has_kra = application['has_kra_pin']
        
        return {
            'check': 'KRA_PIN',
            'verified': bool(has_kra),
            'signal': 'Formal employment likely' if has_kra else 'Informal sector',
            'cost': self.cost_per_check['kra']
        }
    
    def verify_nssf(self, application):
        """
        NSSF Verification
        Cost: KES 5
        Verifies employment
        """
        
        has_nssf = application['has_nssf']
        
        return {
            'check': 'NSSF',
            'verified': bool(has_nssf),
            'signal': 'Active employment' if has_nssf else 'No formal employment',
            'cost': self.cost_per_check['nssf']
        }
    
    def full_verification(self, application):
        """
        Run all Tier 2 checks
        Total cost: KES 20
        """
        
        results = {
            'iprs': self.verify_identity(application),
            'kra': self.verify_kra(application),
            'nssf': self.verify_nssf(application)
        }
        
        # Calculate composite score
        verification_score = 0
        if results['iprs']['verified']:
            verification_score += 40
        if results['kra']['verified']:
            verification_score += 30
        if results['nssf']['verified']:
            verification_score += 30
        
        total_cost = sum(r['cost'] for r in results.values())
        
        # Decision
        if verification_score >= 70:
            decision = 'APPROVE'
        elif verification_score >= 40:
            decision = 'PROCEED_TO_TIER3'
        else:
            decision = 'REJECT'
        
        return {
            'verification_score': verification_score,
            'checks_passed': sum(1 for r in results.values() if r.get('verified', False)),
            'decision': decision,
            'total_cost': total_cost,
            'details': results
        }
    
    def batch_verify(self, df):
        """Verify multiple applications"""
        results = []
        for _, row in df.iterrows():
            result = self.full_verification(row)
            result['application_id'] = row['application_id']
            results.append(result)
        return pd.DataFrame(results)

if __name__ == "__main__":
    df = pd.read_csv('data/raw/loan_applications.csv')
    
    # Only verify those that passed Tier 1
    from tier1_free.risk_scorer import Tier1RiskScorer
    tier1_scorer = Tier1RiskScorer()
    tier1_results = tier1_scorer.batch_score(df)
    
    # Filter to those needing Tier 2
    needs_tier2 = tier1_results[tier1_results['recommendation'] == 'PROCEED_TO_TIER2']['application_id']
    df_tier2 = df[df['application_id'].isin(needs_tier2)]
    
    print(f"Applications needing Tier 2 verification: {len(df_tier2)}")
    
    verifier = Tier2Verifier()
    results = verifier.batch_verify(df_tier2)
    
    print("\nTier 2 Verification Results:")
    print(results['decision'].value_counts())
    print(f"\nTotal Cost: KES {results['total_cost'].sum():,.0f}")
    print(f"Cost per application: KES {results['total_cost'].mean():.0f}")