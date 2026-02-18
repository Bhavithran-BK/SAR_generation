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

class GenerationService:
    def _scrub_pii(self, customer: dict, transactions: list) -> tuple:
        """
        Removes Names, IDs, and other sensitive PII before sending to LLM.
        """
        # Anonymized customer
        anonymized_customer = {
            "account_type": "Retail/Savings", # Generic
            "risk_rating": customer.get("risk_rating", "LOW"),
            "kyc_status": customer.get("kyc_status", "VERIFIED"),
            "region": "India (FIU-IND)"
        }
        
        # Anonymized transactions (removes description names if any, keeps amounts/types)
        anonymized_tx = []
        for tx in transactions:
            anonymized_tx.append({
                "amount": tx.amount,
                "currency": tx.currency,
                "timestamp": tx.timestamp.strftime("%Y-%m-%d"),
                "type": tx.transaction_type,
                "anonymized_description": "Standard Transaction" # Masking specific merchants/names
            })
            
        return anonymized_customer, anonymized_tx

    async def generate_sar(self, request: GenerateRequest) -> SARResponse:
        # 0. Get Region Configuration for context (regulator names etc)
        region_config = RegionFactory.get(request.region)
        
        # 1. Anonymize PII
        customer_data = request.customer.model_dump()
        anon_customer, anon_tx = self._scrub_pii(customer_data, request.transactions)
        
        # 2. Run Rule-Based Analysis
        analysis_results = analysis_engine.analyze(request.transactions)
        
        # 3. Construct HIGH-DETAIL Prompt for LLM
        prompt = f"""
        OFFICIAL SUSPICIOUS ACTIVITY REPORT (SAR) GENERATION REQUEST
        
        CRITICAL PRIVACY RULE: 
        The subject is referred to as "THE ACCOUNT HOLDER". Do NOT use any names or IDs.
        
        SUBJECT PROFILE (Context):
        - Occupation: {request.customer.occupation}
        - Expected Monthly Turnover: {request.customer.expected_monthly_turnover}
        - Risk Rating: {request.customer.risk_rating}
        
        ACTIVITY DATA:
        - Transaction Patterns: {anon_tx}
        - System Alerts: {[a.rule_name for a in request.alerts]}
        
        REPORT REQUIREMENTS:
        The report must follow this structure for clarity:

        SECTION 1: OFFICIAL HEADING
        Title: SUSPICIOUS ACTIVITY REPORT - {region_config.regulator_name}
        Date: {datetime.now().strftime("%Y-%m-%d")}
        
        SECTION 2: EXECUTIVE SUMMARY
        Provide a concise 1-paragraph overview.
        
        SECTION 3: CHRONOLOGY OF ACTIVITY
        List suspicious transactions. Identify if these are consistent with the Subject's Occupation of {request.customer.occupation}.
        
        SECTION 4: BEHAVIORAL ANALYSIS
        Explain if the activity exceeds the Expected Monthly Turnover of {request.customer.expected_monthly_turnover}.
        If the activity appears to be NORMAL (e.g., standard salary, rent, groceries), EXPLICITLY STATE that it may be a false positive.
        If it maps to {request.typology or 'Money Laundering'} typologies, explain why.
        
        SECTION 5: REGULATORY CONCLUSION
        Final assessment on reporting necessity.

        STRICT FORMATTING RULES:
        1. NO MARKDOWN SYMBOLS. Do NOT use '#' for headers. Do NOT use '*' for bold or lists.
        2. Use plain text only. Use "SECTION X:" as headers.
        3. Use standard hyphens (-) for lists.
        4. No "ash symbols" or "asterisks" anywhere in the text.
        """
        
        # 4. Generate Content via LLM
        llm_response = await llm_engine.generate(
            prompt=prompt, 
            system_prompt=f"You are a Senior AML Compliance Officer for {region_config.regulator_name}. Your task is to draft high-quality, legally-sound suspicious activity reports."
        )
        
        sar_id = f"SAR-{uuid.uuid4().hex[:8].upper()}"
        
        # 5. Persist to Database with new states
        async with AsyncSessionLocal() as session:
            db_sar = SAR(
                sar_id=sar_id,
                customer_id=request.customer.customer_id,
                status="GENERATED", # Initial state
                content=llm_response
            )
            session.add(db_sar)
            await session.commit()

        return SARResponse(
            sar_id=sar_id,
            content=llm_response, # AI response is now the whole report
            sections={
                "narrative": llm_response,
                "anonymized_context": str(anon_customer)
            },
            generated_at=datetime.utcnow(),
            status="GENERATED"
        )

generation_service = GenerationService()
