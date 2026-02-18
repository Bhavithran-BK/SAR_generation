import requests
import json
import uuid
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"
API_KEY = "barclays-hackathon-secret-key"

def test_generation_payload():
    print("--- Testing Generation Payload ---")
    
    # 1. Mock Data mimicking Frontend payload
    payload = {
        "customer": {
            "customer_id": "CUST-TEST",
            "name": "Test Customer",
            "account_number": "IN-TEST-001",
            "risk_rating": "HIGH",
            "kyc_status": "VERIFIED"
        },
        "transactions": [
            {
                "transaction_id": str(uuid.uuid4()),
                "amount": 50000.0,
                "currency": "INR",
                "timestamp": datetime.now().isoformat(),
                "sender_account": "IN-TEST-001",
                "receiver_account": "BENEFICIARY",
                "transaction_type": "WIRE",
                "description": "Test Tx 1"
            },
            {
                "transaction_id": str(uuid.uuid4()),
                "amount": 60000.0,
                "currency": "INR",
                "timestamp": datetime.now().isoformat(),
                "sender_account": "IN-TEST-001",
                "receiver_account": "BENEFICIARY",
                "transaction_type": "WIRE",
                "description": "Test Tx 2"
            }
        ],
        "alerts": [],
        "region": "IND",
        "typology": "Suspicious Activity"
    }
    
    print(f"Sending payload with {len(payload['transactions'])} transactions...")
    
    try:
        # 2. Trigger Generation
        res = requests.post(f"{API_URL}/generation/generate", json=payload, headers={"X-API-Key": API_KEY})
        
        if res.status_code == 200:
            data = res.json()
            job_id = data['job_id']
            print(f"✅ Job Submitted: {job_id}")
            
            # 3. Poll for result
            import time
            for i in range(10):
                time.sleep(2)
                status_res = requests.get(f"{API_URL}/generation/status/{job_id}", headers={"X-API-Key": API_KEY})
                status_data = status_res.json()
                print(f"Status: {status_data['status']}")
                
                if status_data['status'] == 'COMPLETED':
                    result = status_data.get('result', {})
                    content = result.get('content', '')
                    sections = result.get('sections', {})
                    auto_analysis = sections.get('automated_analysis', '')
                    
                    print("\n--- Result Analysis ---")
                    print(f"Generated Content Length: {len(content)}")
                    print(f"Automated Analysis details: {auto_analysis}")
                    
                    if "'txn_count': 2" in auto_analysis or "txn_count': 2" in auto_analysis:
                        print("✅ Success: Backend correctly counted 2 transactions.")
                    else:
                        print("❌ Failure: Backend did not count transactions correctly.")
                        print(auto_analysis)
                        
                    if "110000.0" in auto_analysis:
                         print("✅ Success: Backend correctly summed amount (110000.0).")
                    else:
                         print("❌ Failure: Backend sum mismatch.")
                    
                    break
                elif status_data['status'] == 'FAILED':
                    print(f"❌ Job Failed: {status_data.get('error')}")
                    break
        else:
            print(f"❌ Request Failed: {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_generation_payload()
