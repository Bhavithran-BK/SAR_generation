import asyncio
from app.core.llm import llm_engine

async def test_llm():
    print("Testing LLM connectivity...")
    try:
        response = await llm_engine.generate(
            prompt="Hello, are you llama3? Respond with a short sentence.",
            system_prompt="You are a helpful assistant."
        )
        print(f"LLM Response: {response}")
    except Exception as e:
        print(f"LLM Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
