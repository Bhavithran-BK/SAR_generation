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

class GenerationService:
    async def generate_sar(self, request: GenerateRequest) -> SARResponse:
        # 0. Get Region Configuration
        region_config = RegionFactory.get(request.region)
        
        # 1. Run Rule-Based Analysis
        analysis_results = analysis_engine.analyze(request.transactions)
        
        # 2. Construct Prompt for LLM
        prompt = f"""
        Generate a Suspicious Activity Report (SAR) narrative for the following case.
        Focus on the 'Introduction', 'Transaction Analysis', 'Suspicion Details', and 'Conclusion'.
        Do not include headers or formatting, just the raw narrative paragraphs for each section.
        
        Customer: {request.customer.model_dump_json()}
        Transactions: {len(request.transactions)} count. Analysis: {analysis_results}
        Alerts: {[a.rule_name for a in request.alerts]}
        Region: {request.region} ({region_config.report_name})
        Typology: {request.typology}
        """
        
        # 3. Generate Content via LLM
        llm_response = await llm_engine.generate(
            prompt=prompt, 
            system_prompt=f"You are an expert AML compliance analyst for {region_config.regulator_name}."
        )
        
        # 4. Parse LLM response into sections (Mock parsing for now, assuming LLM returns full text)
        # In production, we'd ask LLM to return JSON or specific delimiters.
        # Here we just use the full response as 'narrative' and let the template handle structure.
        narrative_sections = {
            "introduction": llm_response[:500] if len(llm_response) > 500 else llm_response,
            "transaction_analysis": "Detailed analysis of transactions per attached schedule.",
            "conclusion": "Recommendation to file STR based on observable structuring patterns."
        }
        
        # 5. Render Template
        template_name = "india_sar.j2" if request.region in ["IND", "IN"] else "us_sar.j2"
        # Fallback if US template not made yet, use India for demo or generic
        if request.region not in ["IND", "IN"]:
             # For now, just use India one as generic or fail
             template_name = "india_sar.j2" 

        final_content = template_engine.render(template_name, context={
            "request": request,
            "analysis": analysis_results,
            "config": region_config,
            "narrative_sections": narrative_sections,
            "sar_id": f"STR-{uuid.uuid4().hex[:8].upper()}",
            "date": datetime.utcnow().strftime(region_config.date_format)
        })
        
        sections = {
            "narrative": llm_response,
            "automated_analysis": str(analysis_results)
        }
        
        return SARResponse(
            sar_id=f"SAR-{uuid.uuid4().hex[:8].upper()}",
            content=final_content,
            sections=sections,
            generated_at=datetime.utcnow(),
            status="GENERATED"
        )

generation_service = GenerationService()
