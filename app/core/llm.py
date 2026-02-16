import httpx
from app.core.config import settings
import json

class LLMEngine:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = "llama3" # or mistral, can be config

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate text using Ollama asynchronously.
        """
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if system_prompt:
             # Basic template, can be improved
             full_prompt = f"System: {system_prompt}\nUser: {prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client: # Lower timeout for demo
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
             print(f"LLM Generation failed (using mock fallback): {e}")
             return f"[MOCK NARRATIVE] Customer activity analyzed. Suspicious indicators found in transactions exceeding thresholds. Reporting recommended for {system_prompt}."

llm_engine = LLMEngine()
