import sys
import os
import time
import requests

# Add project root to path
sys.path.append(os.getcwd())

from sdk.python.sar_client import SARClient
from app.core.config import settings

def test_full_flow():
    print("🚀 Starting End-to-End System Test...")
    
    # 1. Initialize Client
    client = SARClient(api_key=settings.API_KEY)
    print("✅ Client initialized with API Key.")
    
    # 2. Define Test Data (India Region)
    payload = {
        "customer": {
            "customer_id": "CUST-TEST-001",
            "name": "Test Company Pvt Ltd",
            "email": "test@example.com",
            "account_number": "ACC-IN-12345",
            "risk_rating": "HIGH",
            "kyc_status": "VERIFIED"
        },
        "transactions": [
            {
                "transaction_id": "TXN-001",
                "amount": 1500000.0, # > 10 Lakhs
                "currency": "INR",
                "timestamp": "2023-01-01T10:00:00Z",
                "sender_account": "ACC-IN-12345",
                "receiver_account": "ACC-EXT-999",
                "transaction_type": "NEFT"
            }
        ],
        "alerts": [],
        "region": "IND",
        "typology": "Test Structuring"
    }
    
    # 3. Submit Job
    print("📤 Submitting SAR Generation Job...")
    try:
        response = client.generate_sar(**payload)
        job_id = response["job_id"]
        print(f"✅ Job Submitted! ID: {job_id}")
    except Exception as e:
        print(f"❌ Submission Failed: {e}")
        return

    # 4. Poll for Result
    print("⏳ Polling for results (timeout=60s)...")
    try:
        result = client.wait_for_result(job_id, timeout=60, poll_interval=2)
        print("✅ Job Completed!")
        print("-" * 50)
        print(f"Status: {result['status']}")
        if "result" in result:
             print(f"SAR Content Preview:\n{result['result']['content'][:200]}...")
        else:
             print(f"Error Message: {result.get('error')}")
        print("-" * 50)
        
    except TimeoutError:
        print("❌ Timeout: Job did not complete. Is the Celery worker running?")
    except Exception as e:
        print(f"❌ Polling Failed: {e}")

if __name__ == "__main__":
    test_full_flow()
