import json
import random
from datetime import datetime, timedelta

def generate_negative_samples(count=30):
    occupations = [
        "Software Engineer", "Senior Architect", "Project Manager", 
        "HR Manager", "Marketing Executive", "Sales Director", 
        "Accountant", "Data Scientist", "UI Designer", "Civil Engineer"
    ]
    
    negative_samples = []
    
    for i in range(count):
        case_id = f"NEG-2026-{100 + i}"
        occ = random.choice(occupations)
        salary = random.randint(80000, 250000)
        bonus = round(salary * random.uniform(0.1, 0.3), 0)
        
        # High value but legitimate (Salary + Bonus)
        transactions = [
            {
                "transaction_id": f"TXN-NEG-{i}A",
                "amount": round(salary / 12, 0),
                "currency": "INR" if random.random() > 0.5 else "USD",
                "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
                "transaction_type": "NEFT_CREDIT",
                "description": "MONTHLY SALARY"
            },
            {
                "transaction_id": f"TXN-NEG-{i}B",
                "amount": bonus,
                "currency": "INR" if random.random() > 0.5 else "USD",
                "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
                "transaction_type": "BONUS_PAYMENT",
                "description": "ANNUAL PERFORMANCE BONUS"
            },
            {
                "transaction_id": f"TXN-NEG-{i}C",
                "amount": round(random.uniform(500, 2000), 0),
                "currency": "INR" if random.random() > 0.5 else "USD",
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
                "transaction_type": "POS_DEBIT",
                "description": "SUPERMARKET"
            }
        ]
        
        sample = {
            "case_id": case_id,
            "customer": {
                "name": f"Employee {i}",
                "occupation": occ,
                "risk_rating": "LOW",
                "kyc_status": "VERIFIED"
            },
            "transactions": transactions,
            "alerts": [],
            "risk_analysis": {
                "typology": "NORMAL",
                "risk_score": "LOW"
            },
            "explanation_trace": {
                "triggered_rules": [],
                "key_indicators": [
                    f"Transaction amount aligns with {occ} salary profile",
                    "Clear source of funds (Payroll/Bonus)",
                    "Standard retail expenditure pattern"
                ],
                "reasoning_summary": f"The high-value credit is documented as an annual bonus, which is consistent with the subject's stated occupation of {occ}."
            },
            "expected_sar_narrative": "No suspicious activity detected. The observed transactions, including the larger credit, are consistent with the customer's profile as a salaried professional. The credit is identified as a legitimate bonus payment. No report required."
        }
        negative_samples.append(sample)
    
    return negative_samples

if __name__ == "__main__":
    with open("data/Synthetic_dataset.json", "r") as f:
        original_data = json.load(f)
    
    negatives = generate_negative_samples(30)
    augmented_data = original_data + negatives
    
    with open("data/Augmented_dataset.json", "w") as f:
        json.dump(augmented_data, f, indent=2)
        
    print(f"Generated 30 negative samples and saved to data/Augmented_dataset.json")
