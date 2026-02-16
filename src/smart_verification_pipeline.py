"""
Complete Smart Verification Pipeline
Combines all three tiers
"""

import pandas as pd
import numpy as np
from tier1_free.fraud_detector import Tier1FraudDetector
from tier1_free.risk_scorer import Tier1RiskScorer
from tier2_cheap.verifier import Tier2Verifier
from tier3_expensive.crb_router import Tier3CRBRouter

class SmartVerificationPipeline:
    """
    Complete verification pipeline with cost tracking
    """
    
    def __init__(self):
        self.tier1_fraud = Tier1FraudDetector()
        self.tier1_scorer = Tier1RiskScorer()
        self.tier2_verifier = Tier2Verifier()
        self.tier3_router = Tier3CRBRouter()
    
    def process_single(self, application):
        """
        Process single application through all tiers
        """
        
        result = {
            'application_id': application['application_id'],
            'loan_amount': application['loan_amount']
        }
        
        # TIER 1: FREE CHECKS
        fraud_check = self.tier1_fraud.detect_fraud(application)
        risk_score = self.tier1_scorer.score_application(application)
        
        result['tier1_fraud_score'] = fraud_check['fraud_score']
        result['tier1_risk_score'] = risk_score['tier1_score']
        result['tier1_recommendation'] = risk_score['recommendation']
        result['tier1_cost'] = 0
        
        # Early exit if fraud or auto-approve
        if fraud_check['verdict'] == 'REJECT_FRAUD':
            result['final_decision'] = 'REJECT_FRAUD'
            result['tier2_cost'] = 0
            result['tier3_cost'] = 0
            result['total_cost'] = 0
            result['path'] = 'TIER1_REJECT'
            return result
        
        if risk_score['recommendation'] == 'AUTO_APPROVE':
            result['final_decision'] = 'APPROVE'
            result['tier2_cost'] = 0
            result['tier3_cost'] = 0
            result['total_cost'] = 0
            result['path'] = 'TIER1_APPROVE'
            return result
        
        if risk_score['recommendation'] == 'AUTO_REJECT':
            result['final_decision'] = 'REJECT'
            result['tier2_cost'] = 0
            result['tier3_cost'] = 0
            result['total_cost'] = 0
            result['path'] = 'TIER1_REJECT'
            return result
        
        # TIER 2: CHEAP VERIFICATION
        tier2_result = self.tier2_verifier.full_verification(application)
        result['tier2_score'] = tier2_result['verification_score']
        result['tier2_decision'] = tier2_result['decision']
        result['tier2_cost'] = tier2_result['total_cost']
        
        if tier2_result['decision'] == 'APPROVE':
            result['final_decision'] = 'APPROVE'
            result['tier3_cost'] = 0
            result['total_cost'] = result['tier2_cost']
            result['path'] = 'TIER2_APPROVE'
            return result
        
        if tier2_result['decision'] == 'REJECT':
            result['final_decision'] = 'REJECT'
            result['tier3_cost'] = 0
            result['total_cost'] = result['tier2_cost']
            result['path'] = 'TIER2_REJECT'
            return result
        
        # TIER 3: EXPENSIVE CRB CHECK
        tier3_result = self.tier3_router.process_application(
            application,
            result['tier1_risk_score'],
            result['tier2_score']
        )
        
        result['tier3_checked'] = tier3_result['crb_checked']
        result['tier3_cost'] = tier3_result['tier3_cost']
        result['final_decision'] = tier3_result['decision']
        result['final_score'] = tier3_result['final_score']
        result['total_cost'] = result['tier2_cost'] + result['tier3_cost']
        result['path'] = 'TIER3'
        
        return result
    
    def process_batch(self, df):
        """
        Process multiple applications
        """
        results = []
        for _, row in df.iterrows():
            result = self.process_single(row)
            results.append(result)
        return pd.DataFrame(results)
    
    def generate_cost_report(self, results_df):
        """
        Generate cost comparison report
        """
        
        total_apps = len(results_df)
        
        # Current system cost (check everyone)
        current_system_cost = total_apps * 50  # KES 50 per CRB check
        
        # Our system cost
        our_system_cost = results_df['total_cost'].sum()
        
        # Savings
        savings = current_system_cost - our_system_cost
        savings_pct = (savings / current_system_cost) * 100
        
        # Breakdown
        tier1_only = len(results_df[results_df['tier2_cost'] == 0])
        tier2_reached = len(results_df[results_df['tier2_cost'] > 0])
        tier3_reached = len(results_df[results_df['tier3_cost'] > 0])
        
        report = {
            'total_applications': total_apps,
            'current_system_cost': current_system_cost,
            'our_system_cost': our_system_cost,
            'total_savings': savings,
            'savings_percentage': savings_pct,
            'cost_per_application': our_system_cost / total_apps,
            'tier1_decisions': tier1_only,
            'tier2_decisions': tier2_reached - tier3_reached,
            'tier3_decisions': tier3_reached,
            'tier1_percentage': (tier1_only / total_apps) * 100,
            'tier2_percentage': ((tier2_reached - tier3_reached) / total_apps) * 100,
            'tier3_percentage': (tier3_reached / total_apps) * 100
        }
        
        return report

if __name__ == "__main__":
    # Load data
    df = pd.read_csv('data/raw/loan_applications.csv')
    
    print("="*70)
    print("SMART VERIFICATION PIPELINE")
    print("="*70)
    print(f"\nProcessing {len(df)} applications...")
    
    # Run pipeline
    pipeline = SmartVerificationPipeline()
    results = pipeline.process_batch(df)
    
    # Generate report
    report = pipeline.generate_cost_report(results)
    
    print(f"\n{'='*70}")
    print("COST COMPARISON REPORT")
    print("="*70)
    print(f"\nTotal Applications: {report['total_applications']:,}")
    print(f"\nCURRENT SYSTEM (Check everyone with CRB):")
    print(f"  Cost: KES {report['current_system_cost']:,}")
    print(f"  Per application: KES 50")
    print(f"\nSMART SYSTEM (Tiered approach):")
    print(f"  Total Cost: KES {report['our_system_cost']:,}")
    print(f"  Per application: KES {report['cost_per_application']:.2f}")
    print(f"\nSAVINGS:")
    print(f"  Amount: KES {report['total_savings']:,}")
    print(f"  Percentage: {report['savings_percentage']:.1f}%")
    print(f"\nDECISION BREAKDOWN:")
    print(f"  Tier 1 (FREE): {report['tier1_decisions']:,} ({report['tier1_percentage']:.1f}%)")
    print(f"  Tier 2 (KES 20): {report['tier2_decisions']:,} ({report['tier2_percentage']:.1f}%)")
    print(f"  Tier 3 (KES 50): {report['tier3_decisions']:,} ({report['tier3_percentage']:.1f}%)")
    
    # Save results
    results.to_csv('data/processed/verification_results.csv', index=False)
    print(f"\nResults saved to: data/processed/verification_results.csv")
    print("="*70)
