import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Check if Vertex AI is explicitly disabled. If GCP_PROJECT_ID is not set, disable it.
        self.vertex_enabled = os.getenv("GCP_PROJECT_ID") is not None
        
        # Correctly read the OLLAMA_URL from the .env file.
        # The default value is now correct for our container-to-container setup.
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        
        # Updated the default model to llama3 to match our setup
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "300"))
        
    async def get_response(self, message: str) -> str:
        """Get AI response with Vertex AI primary, Ollama fallback"""
        
        # Try Vertex AI first if it's enabled
        if self.vertex_enabled:
            try:
                response = await self._try_vertex_ai(message)
                if response:
                    logger.info("✅ Vertex AI response successful")
                    return response
            except Exception as e:
                logger.warning(f"❌ Vertex AI failed: {e}")
        
        # Fallback to Ollama
        logger.info("Attempting Ollama fallback...")
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
            if not client or not client.model:
                raise Exception("Vertex AI not initialized")
            
            response = client.generate_response(message)
            if response and len(response.strip()) > 10:
                return response
            raise Exception("Empty Vertex AI response")
        except Exception as e:
            raise Exception(f"Vertex AI error: {e}")
    
    async def _try_ollama(self, message: str) -> str:
        """Try Ollama using the correct /api/chat endpoint."""
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # CORRECT: Use the /api/chat endpoint
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        # CORRECT: Use the 'messages' format for the payload
                        "messages": [
                            {"role": "system", "content": "You are a compassionate AI therapist. Respond with empathy and support. Keep responses to 2-3 sentences."},
                            {"role": "user", "content": message}
                        ],
                        "stream": False
                    }
                )
                response.raise_for_status() # Raises an exception for 4xx/5xx responses
                
                data = response.json()
                
                # CORRECT: Parse the response from the 'message' object
                ai_response = data.get("message", {}).get("content", "").strip()
                
                if not ai_response:
                    raise Exception("Empty Ollama response")
                
                return ai_response

            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Ollama HTTP {e.response.status_code}")
            except Exception as e:
                logger.error(f"An unexpected error occurred with Ollama: {e}")
                raise e

# Global instance
_ai_service = None

def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service