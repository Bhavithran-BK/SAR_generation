import requests
import time
import json
import sys

API_URL = "http://localhost:8000/api/v1"
API_KEY = "barclays-hackathon-secret-key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def run_validation():
    print("1. Fetching Cases...")
    try:
        res = requests.get(f"{API_URL}/cases", headers=HEADERS)
        res.raise_for_status()
        cases = res.json().get("cases", [])
        if not cases:
            print("FAILED: No cases found.")
            return
        
        target_case_num = "IN-882299"
        target_case = next((c for c in cases if c["account_number"] == target_case_num), cases[0])
        print(f"   Selected Case: {target_case['account_number']}")
    except Exception as e:
        print(f"FAILED: Could not fetch cases. {e}")
        return

    print("\n2. Fetching Case Details...")
    try:
        res = requests.get(f"{API_URL}/cases/{target_case['account_number']}", headers=HEADERS)
        res.raise_for_status()
        details = res.json()
        print(f"   Customer: {details['customer']['name']}")
        print(f"   Transactions: {len(details['transactions'])}")
        
        # Select all transactions
        selected_tx = details['transactions']
    except Exception as e:
        print(f"FAILED: Could not fetch details. {e}")
        return

    print("\n3. Triggering Generation...")
    payload = {
        "customer": details['customer'],
        "transactions": selected_tx,
        "alerts": details['alerts'],
        "region": "IND",
        "typology": "Suspicious Activity"
    }
    
    try:
        res = requests.post(f"{API_URL}/generation/generate", headers=HEADERS, json=payload)
        res.raise_for_status()
        job_id = res.json()['job_id']
        print(f"   Job ID: {job_id}")
    except Exception as e:
        print(f"FAILED: Generation trigger failed. {e}")
        return

    print("\n4. Polling for Completion...")
    status = "PROCESSING"
    sar_id = None
    content = None
    
    while status in ["PENDING", "PROCESSING"]:
        time.sleep(2)
        try:
            res = requests.get(f"{API_URL}/generation/status/{job_id}", headers=HEADERS)
            data = res.json()
            status = data['status']
            print(f"   Status: {status}")
            
            if status == "COMPLETED":
                sar_id = data['result']['sar_id']
                content = data['result']['content']
            elif status == "FAILED":
                print(f"FAILED: Generation job failed. {data.get('error')}")
                return
        except Exception as e:
            print(f"polling error: {e}")
            break

    print("\n5. Generated Content Snippet:")
    print("-" * 40)
    print(content[:500] + "..." if content else "NO CONTENT")
    print("-" * 40)

    if sar_id:
        print(f"\n6. Finalizing SAR {sar_id}...")
        try:
            # Save
            res = requests.post(f"{API_URL}/generation/save/{sar_id}", headers=HEADERS, params={"edited_content": content})
            res.raise_for_status()
            
            # Finalize
            res = requests.post(f"{API_URL}/generation/finalize/{sar_id}", headers=HEADERS, params={"reviewer": "Automated_Test"})
            res.raise_for_status()
            print("   SUCCESS: Follow completely verified.")
        except Exception as e:
            print(f"FAILED: Finalization failed. {e}")

if __name__ == "__main__":
    try:
        run_validation()
    except KeyboardInterrupt:
        print("\nAborted.")
