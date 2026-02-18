import httpx
from app.core.config import settings
import json

class LLMEngine:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = "llama3:latest" # Use specific tag

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate text using Ollama asynchronously.
        """
        url = f"{self.base_url}/api/generate"
        
        # Standard Ollama JSON payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            # Use 127.0.0.1 for stability and longer timeout
            # On Windows, localhost can sometimes be flaky with httpx
            target_url = url.replace("localhost", "127.0.0.1")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                print(f"Ollama Request: {self.model} at {target_url}", flush=True)
                response = await client.post(target_url, json=payload)
                response.raise_for_status()
                result = response.json()
                text = result.get("response", "")
                print(f"Ollama Response (Proof Check): {text[:100]}...", flush=True)
                return text
                
        except Exception as e:
            print(f"Ollama connection error (127.0.0.1): {e}", flush=True)
            # Fallback to original base_url (localhost) as a second attempt
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    print(f"Ollama Retry: {self.model} at {url}", flush=True)
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    return result.get("response", "")
            except Exception as e2:
                print(f"LLM Generation failed entirely: {e2}", flush=True)
                # DO NOT RETURN MOCK DATA. The system should show error or stall.
                raise Exception(f"AI Generation Failed: {str(e2)}. Ensure Ollama is running.")

llm_engine = LLMEngine()
