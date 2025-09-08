import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.vertex_enabled = os.getenv("USE_VERTEX_AI", "true").lower() == "true"
        self.ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "30"))
        
    async def get_response(self, message: str) -> str:
        """Get AI response with Vertex AI primary, Ollama fallback"""
        
        # Try Vertex AI first
        if self.vertex_enabled:
            try:
                response = await self._try_vertex_ai(message)
                if response:
                    logger.info("✅ Vertex AI response successful")
                    return response
            except Exception as e:
                logger.warning(f"❌ Vertex AI failed: {e}")
        
        # Fallback to Ollama
        try:
            response = await self._try_ollama(message)
            logger.info("✅ Ollama fallback successful")
            return response
        except Exception as e:
            logger.error(f"❌ Ollama fallback failed: {e}")
            raise Exception("All AI services unavailable")
    
    async def _try_vertex_ai(self, message: str) -> Optional[str]:
        """Try Vertex AI"""
        try:
            from .vertex_ai import get_vertex_client
            client = get_vertex_client()
            if not client.model:
                raise Exception("Vertex AI not initialized")
            
            response = client.generate_response(message)
            if response and len(response.strip()) > 10:
                return response
            raise Exception("Empty Vertex AI response")
        except Exception as e:
            raise Exception(f"Vertex AI error: {e}")
    
    async def _try_ollama(self, message: str) -> str:
        """Try Ollama"""
        prompt = f"You are a compassionate AI therapist. Respond with empathy and support. Keep responses to 2-3 sentences.\n\nUser: {message}\n\nTherapist:"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama HTTP {response.status_code}")
            
            data = response.json()
            ai_response = data.get("response", "").strip()
            
            if not ai_response:
                raise Exception("Empty Ollama response")
            
            return ai_response

# Global instance
_ai_service = None

def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service