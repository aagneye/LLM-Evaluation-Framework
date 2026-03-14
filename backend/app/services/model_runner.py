import time
from typing import Dict, Any
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


class ModelRunner:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def run_prompt(self, prompt: str, model_name: str) -> Dict[str, Any]:
        """
        Run a prompt against a specified model and return response with latency.
        """
        start_time = time.time()
        
        try:
            if model_name.startswith("gpt"):
                response = self._run_openai(prompt, model_name)
            else:
                response = self._run_local_model(prompt, model_name)
            
            latency = time.time() - start_time
            
            return {
                "response_text": response,
                "latency": latency,
                "success": True
            }
        except Exception as e:
            latency = time.time() - start_time
            return {
                "response_text": f"Error: {str(e)}",
                "latency": latency,
                "success": False
            }
    
    def _run_openai(self, prompt: str, model_name: str) -> str:
        """Run prompt using OpenAI API."""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    def _run_local_model(self, prompt: str, model_name: str) -> str:
        """
        Placeholder for local model execution.
        In production, this would integrate with Ollama, vLLM, or other local inference.
        """
        return f"[Local model {model_name} response placeholder for: {prompt[:50]}...]"
