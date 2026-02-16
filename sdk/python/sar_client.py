import requests
import time
from typing import Dict, Any, List

class SARClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1", api_key: str = None):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["X-API-Key"] = api_key

    def generate_sar(self, customer: Dict, transactions: List[Dict], alerts: List[Dict], region: str = "US", typology: str = None) -> Dict:
        """Submit a SAR generation job."""
        payload = {
            "customer": customer,
            "transactions": transactions,
            "alerts": alerts,
            "region": region,
            "typology": typology
        }
        response = requests.post(f"{self.base_url}/generation/generate", json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_status(self, job_id: str) -> Dict:
        """Poll job status."""
        response = requests.get(f"{self.base_url}/generation/status/{job_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_result(self, job_id: str, timeout: int = 60, poll_interval: int = 2) -> Dict:
        """Poll until completion or timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)
            if status["status"] in ["COMPLETED", "FAILED"]:
                return status
            time.sleep(poll_interval)
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
