from typing import List, Dict, Any
from app.schemas.models import Transaction, Alert
from datetime import timedelta

class AnalysisEngine:
    """
    Rule-based engine to detect suspicious patterns before AI generation.
    """
    
    def detect_structuring(self, transactions: List[Transaction]) -> List[Dict]:
        """
        Detect transactions just below reporting thresholds (e.g., $10,000).
        """
        suspicious = []
        for txn in transactions:
            if 9000 <= txn.amount < 10000:
                suspicious.append({
                    "type": "Structuring",
                    "transaction_id": txn.transaction_id,
                    "reason": f"Amount ${txn.amount} is just below $10,000 threshold."
                })
        return suspicious

    def detect_rapid_movement(self, transactions: List[Transaction]) -> List[Dict]:
        """
        Detect rapid in/out movement (mock logic for now).
        """
        # Complex logic would go here (sorting by time, checking balance)
        # For prototype, we check if multiple large transactions occur same day
        if len(transactions) < 2:
            return []
            
        sorted_txns = sorted(transactions, key=lambda x: x.timestamp)
        suspicious = []
        
        for i in range(len(sorted_txns) - 1):
            t1 = sorted_txns[i]
            t2 = sorted_txns[i+1]
            
            if (t2.timestamp - t1.timestamp) < timedelta(hours=24) and t1.amount > 5000 and t2.amount > 5000:
                 suspicious.append({
                    "type": "Rapid Movement",
                    "ids": [t1.transaction_id, t2.transaction_id],
                    "reason": "Large transactions within 24 hours."
                })
        return suspicious

    def analyze(self, transactions: List[Transaction]) -> Dict[str, Any]:
        return {
            "structuring": self.detect_structuring(transactions),
            "rapid_movement": self.detect_rapid_movement(transactions),
            "total_volume": sum(t.amount for t in transactions),
            "txn_count": len(transactions)
        }

analysis_engine = AnalysisEngine()
