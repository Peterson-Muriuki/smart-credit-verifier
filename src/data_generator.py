"""
Smart Verification Data Generator
Generates sample loan applications with verification signals
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

np.random.seed(42)
random.seed(42)
fake = Faker()

def generate_applications(n=10000):
    """
    Generate loan applications with free and paid verification signals
    """
    
    print("="*70)
    print("GENERATING LOAN APPLICATIONS")
    print("="*70)
    
    data = []
    
    for i in range(n):
        # Basic info
        applicant_type = random.choices(
            ['legitimate', 'fraudster', 'risky', 'good_repeat'],
            weights=[0.50, 0.15, 0.25, 0.10]
        )[0]
        
        # Free Tier 1 Signals
        device_age_months = np.random.exponential(18)
        sim_age_months = np.random.exponential(24)
        
        if applicant_type == 'fraudster':
            device_age_months = random.uniform(0, 3)
            sim_age_months = random.uniform(0, 2)
            completion_time = random.uniform(30, 120)  # Rushed
            applications_24h = random.randint(3, 10)
            copy_paste_count = random.randint(5, 15)
        else:
            completion_time = random.uniform(300, 900)  # Normal
            applications_24h = 1
            copy_paste_count = random.randint(0, 2)
        
        # Location
        location = random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Rural'])
        gps_matches_address = random.random() > 0.05 if applicant_type != 'fraudster' else random.random() > 0.5
        
        # Phone signals
        line_type = random.choice(['prepaid', 'postpaid'])
        if line_type == 'postpaid':
            creditworthy_boost = 0.15
        else:
            creditworthy_boost = 0
        
        # Behavioral signals
        application_hour = int(np.random.normal(14, 3)) if applicant_type != 'fraudster' else random.randint(0, 6)
        application_hour = max(0, min(23, application_hour))
        
        # Device value indicator
        device_value = random.choice(['low', 'medium', 'high'])
        device_value_ksh = {'low': 5000, 'medium': 20000, 'high': 60000}[device_value]
        
        # Tier 2 Signals (would cost KES 10-20)
        has_kra_pin = random.random() > 0.40
        has_nssf = random.random() > 0.50
        iprs_verified = random.random() > 0.05
        
        # Tier 3 Signals (would cost KES 50+)
        has_crb_record = random.random() > 0.65
        crb_score = int(np.random.normal(500, 100)) if has_crb_record else 0
        crb_score = max(300, min(700, crb_score))
        
        if applicant_type == 'fraudster':
            has_crb_record = False
            has_kra_pin = False
            has_nssf = False
        
        # Loan details
        loan_amount = random.choice([1000, 2000, 3000, 5000, 10000, 15000, 20000])
        loan_term_days = random.choice([7, 14, 30, 60, 90])
        
        # Income
        employment_type = random.choice(['formal', 'informal', 'self_employed', 'unemployed'])
        if employment_type == 'formal':
            monthly_income = random.uniform(20000, 80000)
        elif employment_type == 'self_employed':
            monthly_income = random.uniform(15000, 60000)
        elif employment_type == 'informal':
            monthly_income = random.uniform(10000, 40000)
        else:
            monthly_income = random.uniform(5000, 20000)
        
        # Determine actual outcome
        if applicant_type == 'fraudster':
            should_approve = False
            will_default = True
        elif applicant_type == 'good_repeat':
            should_approve = True
            will_default = False
        elif applicant_type == 'legitimate':
            risk_score = (
                (1 if has_crb_record else 0) * 0.3 +
                (crb_score / 700 if has_crb_record else 0.5) * 0.3 +
                (sim_age_months / 60) * 0.2 +
                creditworthy_boost +
                (1 if has_kra_pin else 0) * 0.1
            )
            should_approve = risk_score > 0.5
            will_default = random.random() > (0.85 + risk_score * 0.1)
        else:  # risky
            should_approve = random.random() > 0.5
            will_default = random.random() > 0.7
        
        record = {
            'application_id': f'APP_{i+1:06d}',
            'applicant_type': applicant_type,
            'timestamp': (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S'),
            
            # FREE TIER 1 SIGNALS
            'device_age_months': round(device_age_months, 1),
            'sim_age_months': round(sim_age_months, 1),
            'completion_time_seconds': int(completion_time),
            'application_hour': application_hour,
            'applications_last_24h': applications_24h,
            'copy_paste_count': copy_paste_count,
            'gps_matches_address': int(gps_matches_address),
            'device_value': device_value,
            'device_value_ksh': device_value_ksh,
            'line_type': line_type,
            
            # CHEAP TIER 2 SIGNALS (KES 10-20)
            'has_kra_pin': int(has_kra_pin),
            'has_nssf': int(has_nssf),
            'iprs_verified': int(iprs_verified),
            
            # EXPENSIVE TIER 3 SIGNALS (KES 50)
            'has_crb_record': int(has_crb_record),
            'crb_score': crb_score,
            
            # APPLICATION DATA
            'loan_amount': loan_amount,
            'loan_term_days': loan_term_days,
            'monthly_income': round(monthly_income, 2),
            'employment_type': employment_type,
            'location': location,
            
            # OUTCOMES
            'should_approve': int(should_approve),
            'will_default': int(will_default),
        }
        
        data.append(record)
    
    df = pd.DataFrame(data)
    
    print(f"\nGenerated {len(df)} applications")
    print(f"\nDistribution:")
    print(df['applicant_type'].value_counts())
    print(f"\nShould Approve: {df['should_approve'].sum()} ({df['should_approve'].mean()*100:.1f}%)")
    print(f"Will Default: {df['will_default'].sum()} ({df['will_default'].mean()*100:.1f}%)")
    
    return df

if __name__ == "__main__":
    df = generate_applications(10000)
    df.to_csv('data/raw/loan_applications.csv', index=False)
    print(f"\nSaved to: data/raw/loan_applications.csv")
    print("="*70)