import asyncio
import random
from app.schemas.requests import GenerateRequest
from app.schemas.responses import SARResponse
from datetime import datetime
import uuid

from app.core.llm import llm_engine
from app.services.analysis_engine import analysis_engine
from app.core.region_config import RegionFactory
from app.services.template_engine import template_engine
from app.db.base import AsyncSessionLocal
from app.models.sql import SAR

from app.utils.privacy_guard import NarrativeStitcher, PrivacyGuard

class GenerationService:
    def _prepare_anonymized_data(self, request: GenerateRequest) -> dict:
        """
        Creates a version of the data where PII is replaced by placeholders.
        """
        anonymized_tx = []
        for tx in request.transactions:
            anonymized_tx.append({
                "amount": tx.amount,
                "currency": tx.currency,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d"),
                "type": tx.transaction_type,
                "desc": "Standard Transaction" # Masking specific merchants/names
            })
            
        return {
            "customer": {
                "name": "{{CUSTOMER_NAME}}",
                "id": "{{CUSTOMER_ID}}",
                "occupation": request.customer.occupation,
                "risk_rating": request.customer.risk_rating
            },
            "transactions": anonymized_tx,
            "alerts": [a.rule_name for a in request.alerts]
        }

    async def generate_sar(self, request: GenerateRequest) -> SARResponse:
        # 1. Prepare anonymized context
        anon_data = self._prepare_anonymized_data(request)
        
        # 2. Extract real PII for post-processing
        pii_map = {
            "name": request.customer.name,
            "customer_id": request.customer.customer_id,
            "account": "ACC-XXXX-" + str(uuid.uuid4().hex[:4]), # Mocking account if missing
            "country": "India",
            "case_id": f"CASE-{uuid.uuid4().hex[:6].upper()}"
        }
        
        # 3. Construct Privacy-Safe Prompt
        system_prompt = (
            "You are a senior AML Compliance Officer. Draft a professional SAR narrative. "
            "PRIVACY RULE: NEVER use real names or IDs. Use ONLY standardized placeholders: "
            "{{CUSTOMER_NAME}}, {{ACCOUNT_NUMBER}}, {{CUSTOMER_ID}}, {{COUNTRY}}, {{CASE_ID}}. "
            "If no suspicious alerts are present, output: 'No suspicious activity identified for {{CUSTOMER_NAME}} during the review period.'"
        )
        
        user_prompt = f"""
        INVESTIGATION FOR CASE {{{{CASE_ID}}}}
        
        SUBJECT PROFILE:
        - Name: {{{{CUSTOMER_NAME}}}}
        - Occupation: {anon_data['customer']['occupation']}
        - Risk Rating: {anon_data['customer']['risk_rating']}
        
        ACTIVITY SUMMARY:
        - Alerts: {anon_data['alerts']}
        - Transactions: {anon_data['transactions'][:10]} (Sample size: {len(anon_data['transactions'])})
        
        TASK:
        Draft a concise the Suspicious Activity Report (SAR) narrative. Ground your reasoning 
        strictly in the triggered rules and indicators. Ensure placeholders are used accurately.
        """
        
        # 4. Generate Anonymized Narrative via LLM
        # Using a timeout safety checked llama3:latest
        raw_narrative = await llm_engine.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # 5. Post-Processing: PII Injection & Leakage Check
        if PrivacyGuard.check_leakage(raw_narrative, [request.customer.name, request.customer.customer_id]):
            # Emergency fix: force re-anonymization if model slipped
            raw_narrative = raw_narrative.replace(request.customer.name, "{{CUSTOMER_NAME}}")
        
        final_narrative = NarrativeStitcher.stitch(raw_narrative, pii_map)
        
        # 6. Persist to Database
        sar_id = pii_map["case_id"]
        async with AsyncSessionLocal() as session:
            db_sar = SAR(
                sar_id=sar_id,
                customer_id=request.customer.customer_id,
                status="GENERATED",
                content=final_narrative
            )
            session.add(db_sar)
            await session.commit()
 
        return SARResponse(
            sar_id=sar_id,
            content=final_narrative,
            sections={
                "narrative": final_narrative,
                "anonymized_query": user_prompt
            },
            generated_at=datetime.utcnow(),
            status="GENERATED"
        )

generation_service = GenerationService()
