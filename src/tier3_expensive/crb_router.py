"""
Tier 3: Expensive CRB Check Router - STANDALONE VERSION
Only check CRB when truly necessary
Cost: KES 50 per check

This version includes Tier1 scorer inline to avoid import issues
"""

import pandas as pd
import numpy as np

# ============================================================================
# TIER 1 RISK SCORER (Embedded)
# ============================================================================
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


# ============================================================================
# TIER 3 CRB ROUTER
# ============================================================================
class Tier3CRBRouter:
    """
    Smart routing to expensive CRB checks
    Cost: KES 50 per check
    """
    
    def __init__(self):
        self.crb_cost = 50
    
    def should_check_crb(self, application, tier1_score, tier2_score):
        """
        Decide if CRB check is worth the cost
        """
        
        # Rule 1: High-value loans always check
        if application['loan_amount'] >= 15000:
            return True, "High-value loan (>= KES 15,000)"
        
        # Rule 2: Borderline scores need tie-breaker
        if 45 <= tier1_score <= 65 and 40 <= tier2_score <= 70:
            return True, "Borderline scores need CRB tie-breaker"
        
        # Rule 3: No CRB for obvious rejects
        if tier1_score < 30:
            return False, "Tier 1 score too low (fraud likely)"
        
        # Rule 4: No CRB for excellent Tier 1 + Tier 2
        if tier1_score >= 75 and tier2_score >= 70:
            return False, "Excellent free+cheap signals, CRB unnecessary"
        
        # Rule 5: Check if conflicting signals
        if abs(tier1_score - tier2_score) > 30:
            return True, "Conflicting signals between Tier 1 and Tier 2"
        
        # Default: Don't check
        return False, "Sufficient data from Tier 1 and Tier 2"
    
    def perform_crb_check(self, application):
        """
        Simulate CRB check (would be API call in production)
        Cost: KES 50
        """
        
        has_crb = application['has_crb_record']
        crb_score = application['crb_score'] if has_crb else 0
        
        if not has_crb:
            return {
                'has_record': False,
                'score': 0,
                'signal': 'No CRB record (unbanked)',
                'cost': self.crb_cost
            }
        
        # Interpret CRB score
        if crb_score >= 650:
            signal = 'Excellent credit history'
            boost = 20
        elif crb_score >= 550:
            signal = 'Good credit history'
            boost = 10
        elif crb_score >= 450:
            signal = 'Fair credit history'
            boost = 0
        else:
            signal = 'Poor credit history'
            boost = -20
        
        return {
            'has_record': True,
            'score': crb_score,
            'signal': signal,
            'score_boost': boost,
            'cost': self.crb_cost
        }
    
    def final_decision(self, application, tier1_score, tier2_score, tier3_result=None):
        """
        Make final lending decision
        """
        
        # Start with Tier 1 + Tier 2 scores
        base_score = (tier1_score * 0.4 + tier2_score * 0.6)
        
        # Add Tier 3 if available
        if tier3_result and tier3_result.get('has_record'):
            crb_contribution = tier3_result.get('score_boost', 0)
            final_score = base_score + crb_contribution
        else:
            final_score = base_score
        
        # Ensure 0-100
        final_score = max(0, min(100, final_score))
        
        # Decision thresholds
        if final_score >= 70:
            decision = 'APPROVE'
            recommended_amount = application['loan_amount']
        elif final_score >= 55:
            decision = 'APPROVE_REDUCED'
            recommended_amount = application['loan_amount'] * 0.7
        else:
            decision = 'REJECT'
            recommended_amount = 0
        
        return {
            'final_score': final_score,
            'decision': decision,
            'recommended_amount': recommended_amount
        }
    
    def process_application(self, application, tier1_score, tier2_score):
        """
        Complete Tier 3 processing
        """
        
        # Decide if CRB check needed
        needs_crb, reason = self.should_check_crb(application, tier1_score, tier2_score)
        
        cost = 0
        tier3_result = None
        
        if needs_crb:
            tier3_result = self.perform_crb_check(application)
            cost = tier3_result['cost']
        
        # Final decision
        final = self.final_decision(application, tier1_score, tier2_score, tier3_result)
        
        return {
            'application_id': application['application_id'],
            'crb_checked': needs_crb,
            'crb_reason': reason,
            'tier3_cost': cost,
            'tier3_result': tier3_result,
            **final
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    import os
    
    print("=" * 70)
    print("TIER 3 CRB ROUTER - COST OPTIMIZATION DEMO")
    print("=" * 70)
    
    # Check if data file exists
    data_path = 'data/raw/loan_applications.csv'
    if not os.path.exists(data_path):
        print(f"\n❌ ERROR: Data file not found at {data_path}")
        print("\nPlease ensure:")
        print("1. You're running from project root: C:\\smart-credit-verify")
        print("2. The data file exists at: data/raw/loan_applications.csv")
        print("\nRun: python src\\tier3_expensive\\crb_router.py")
        exit(1)
    
    # Load data
    print(f"\n Loading applications from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} applications")
    
    # Run Tier 1 scoring
    print("\n TIER 1: Free Risk Scoring (KES 0)...")
    tier1_scorer = Tier1RiskScorer()
    tier1_results = tier1_scorer.batch_score(df)
    print(f" Scored {len(tier1_results)} applications")
    
    # Merge Tier 1 scores
    df = df.merge(tier1_results[['application_id', 'tier1_score', 'recommendation']], 
                  on='application_id')
    
    # Process with Tier 3 router
    print("\n TIER 3: Smart CRB Routing (KES 50 per check)...")
    router = Tier3CRBRouter()
    results = []
    
    for _, row in df.iterrows():
        # Simulate Tier 2 score (in production, this would come from Tier2Verifier)
        tier2_score = 60 if (row.get('has_kra_pin', False) or row.get('has_nssf', False)) else 40
        
        result = router.process_application(row, row['tier1_score'], tier2_score)
        results.append(result)
    
    results_df = pd.DataFrame(results)
    
    # Calculate savings
    total_apps = len(results_df)
    crb_checked = results_df['crb_checked'].sum()
    crb_avoided = total_apps - crb_checked
    
    current_approach_cost = total_apps * 50  # Check everyone
    smart_approach_cost = results_df['tier3_cost'].sum()
    savings = current_approach_cost - smart_approach_cost
    savings_pct = (savings / current_approach_cost) * 100
    
    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n CRB Check Statistics:")
    print(f"   Total Applications:     {total_apps:,}")
    print(f"   CRB Checks Performed:   {crb_checked:,} ({crb_checked/total_apps*100:.1f}%)")
    print(f"   CRB Checks Avoided:     {crb_avoided:,} ({crb_avoided/total_apps*100:.1f}%)")
    
    print(f"\n Cost Comparison:")
    print(f"   Current Approach:       KES {current_approach_cost:,} (check everyone)")
    print(f"   Smart Routing:          KES {smart_approach_cost:,} (selective)")
    print(f"   Savings:                KES {savings:,} ({savings_pct:.1f}%)")
    
    print(f"\n Final Decisions:")
    decision_counts = results_df['decision'].value_counts()
    for decision, count in decision_counts.items():
        print(f"   {decision:20s} {count:,} ({count/total_apps*100:.1f}%)")
    
    print(f"\n📈 Average Final Score: {results_df['final_score'].mean():.1f}/100")
    
    # Save results
    output_path = 'data/processed/tier3_crb_results.csv'
    os.makedirs('data/processed', exist_ok=True)
    results_df.to_csv(output_path, index=False)
    print(f"\n Results saved to: {output_path}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)