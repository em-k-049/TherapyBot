import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """Ollama client for local AI model fallback"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = 30.0
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Ollama local model"""
        try:
            therapeutic_prompt = f"""You are a compassionate AI therapist. Respond with empathy and support. Keep responses to 2-3 sentences.

User: {prompt}

Therapist:"""
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": therapeutic_prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    generated_text = data.get("response", "").strip()
                    if generated_text:
                        logger.info(f"Successfully generated Ollama response: {len(generated_text)} chars")
                        return generated_text
                    else:
                        raise Exception("Empty response from Ollama")
                else:
                    raise Exception(f"Ollama returned status {response.status_code}: {response.text}")
                
        except httpx.TimeoutException as e:
            logger.error(f"Ollama timeout: {e}")
            raise Exception(f"Ollama timeout: {e}")
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection error: {e}")
            raise Exception(f"Ollama connection error: {e}")
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            raise Exception(f"Ollama error: {e}")
    
    def _get_fallback_response(self, message: str) -> str:
        """Basic fallback when both AI services fail"""
        return "I'm here to listen and support you. Can you tell me more about how you're feeling?"

# Global client instance
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client

async def get_ollama_response(message: str) -> str:
    """Get response from Ollama"""
    client = get_ollama_client()
    return await client.generate_response(message)