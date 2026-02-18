import json

def anonymize_text(text, entry):
    """
    Replaces real PII with placeholders in the given text based on entry data.
    """
    if not text:
        return ""
    
    customer = entry.get("customer", {})
    name = customer.get("name")
    case_id = entry.get("case_id")
    
    anonymized = text
    
    # Replace Name
    if name:
        anonymized = anonymized.replace(name, "{{CUSTOMER_NAME}}")
    
    # Replace Case ID
    if case_id:
        anonymized = anonymized.replace(case_id, "{{CASE_ID}}")
        
    # Standardize country and account since they aren't explicitly structured in current JSON
    # but might appear in narrative. We look for common patterns or just use placeholders in input.
    return anonymized

def format_for_sft(input_file, output_file):
    with open(input_file, "r") as f:
        data = json.load(f)
    
    formatted_data = []
    
    instruction = (
        "You are an AML Investigator. Draft a SAR narrative using strictly grounded reasoning. "
        "PRIVACY RULE: NEVER use real names or IDs. Use ONLY standardized placeholders: "
        "{{CUSTOMER_NAME}}, {{ACCOUNT_NUMBER}}, {{CUSTOMER_ID}}, {{COUNTRY}}, {{CASE_ID}}."
    )
    
    for entry in data:
        customer = entry.get("customer", {})
        # Use placeholders for input to ensure model never even sees the real PII if possible
        # However, for training, we want the model to learn to output placeholders even if name is in input.
        # But per user request, we DO NOT send PII to LLM. 
        # So training data input should ALSO use placeholders.
        
        cust_str = f"Name: {{{{CUSTOMER_NAME}}}}, Occupation: {customer.get('occupation', 'N/A')}, Risk Rating: {customer.get('risk_rating')}"
        
        txns = entry.get("transactions", [])
        tx_str = "; ".join([
            f"{tx.get('timestamp', 'N/A')[:10]}: {tx.get('amount', 0)} {tx.get('currency', 'UNK')} ({tx.get('transaction_type', 'N/A')})" 
            for tx in txns
        ])
        
        alerts = entry.get("alerts", [])
        alert_str = ", ".join([a['rule_name'] for a in alerts]) if alerts else "No alerts triggered"
        
        trace = entry.get("explanation_trace", {})
        indicators = ", ".join(trace.get("key_indicators", []))
        summary = trace.get("reasoning_summary", "")
        trace_str = f"Indicators: {indicators}. Summary: {summary}"
        
        input_text = f"Customer: {cust_str}\nTransactions: {tx_str}\nAlerts: {alert_str}\nReasoning Trace: {trace_str}"
        
        # Anonymize output text (the expected narrative)
        output_text = anonymize_text(entry.get("expected_sar_narrative", ""), entry)
        
        formatted_entry = {
            "instruction": instruction,
            "input": input_text,
            "output": output_text
        }
        formatted_data.append(formatted_entry)
    
    with open(output_file, "w") as f:
        for entry in formatted_data:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Formatted {len(formatted_data)} entries into {output_file}")

if __name__ == "__main__":
    format_for_sft("data/Augmented_dataset.json", "data/sar_sft_train.jsonl")
