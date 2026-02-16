import json
import random
import csv
from datetime import datetime, timedelta
import uuid

def generate_random_data(num_requests=5):
    requests = []
    
    for _ in range(num_requests):
        customer_id = f"CUST-{random.randint(10000, 99999)}"
        account_number = f"ACC-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        customer = {
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "email": f"user{customer_id}@example.com",
            "account_number": account_number,
            "risk_rating": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "kyc_status": "VERIFIED"
        }
        
        transactions = []
        base_time = datetime.utcnow()
        for i in range(random.randint(3, 10)):
            txn_time = base_time - timedelta(days=random.randint(0, 30))
            transactions.append({
                "transaction_id": f"TXN-{uuid.uuid4().hex[:8]}",
                "amount": round(random.uniform(1000, 50000), 2),
                "currency": "USD",
                "timestamp": txn_time.isoformat(),
                "sender_account": account_number,
                "receiver_account": f"ACC-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "description": random.choice(["Payment", "Transfer", "Consulting", "Service", "Purchase"]),
                "transaction_type": random.choice(["WIRE", "ACH", "TRANSFER"])
            })
            
        alerts = []
        if random.random() > 0.5:
            alerts.append({
                "alert_id": f"ALT-{uuid.uuid4().hex[:8]}",
                "rule_name": random.choice(["Structuring", "Rapid Movement", "High Return"]),
                "severity": random.choice(["HIGH", "MEDIUM"]),
                "timestamp": datetime.utcnow().isoformat(),
                "details": {"reason": "Auto-generated alert"}
            })
            
        requests.append({
            "customer": customer,
            "transactions": transactions,
            "alerts": alerts,
            "region": "US",
            "typology": random.choice(["Structuring", "Smurfing", "Layering"]) if alerts else None
        })
        
    return requests

if __name__ == "__main__":
    data = generate_random_data(10)
    
    # Save as JSON
    with open("data/test_data_batch.json", "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Generated {len(data)} requests in data/test_data_batch.json")
