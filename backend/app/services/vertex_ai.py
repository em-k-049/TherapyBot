import os
import logging
from typing import Optional

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    GenerativeModel = None
    GenerationConfig = None

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Google Cloud Vertex AI client for generating therapeutic responses"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.region = os.getenv("GCP_REGION", "us-central1")
        self.model_name = os.getenv("VERTEX_AI_MODEL", "gemini-2.0-flash")
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Vertex AI client"""
        if not VERTEX_AI_AVAILABLE:
            logger.warning("Vertex AI not available, using fallback responses only")
            self.model = None
            return
            
        try:
            if not self.project_id:
                logger.warning("GCP_PROJECT_ID not set, using fallback responses")
                self.model = None
                return
            
            # Set credentials if available
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                logger.info(f"Using credentials from: {credentials_path}")
            
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.region)
            
            # Initialize the generative model
            self.model = GenerativeModel(
                model_name=self.model_name,
                generation_config=GenerationConfig(
                    temperature=float(os.getenv("VERTEX_AI_TEMPERATURE", "0.7")),
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=int(os.getenv("VERTEX_AI_MAX_TOKENS", "1024")),
                )
            )
            
            logger.info(f"Vertex AI initialized successfully - Project: {self.project_id}, Model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.model = None
    
    def generate_response(self, prompt: str) -> str:
        """Generate therapeutic response using Vertex AI"""
        if not self.model:
            logger.warning("Vertex AI not available")
            raise Exception("Vertex AI model not initialized")
        
        try:
            # Create therapeutic context for the prompt
            therapeutic_prompt = f"""
You are a compassionate AI therapist providing mental health support. 
Respond with empathy, active listening, and therapeutic techniques.
Keep responses supportive, non-judgmental, and encourage professional help when needed.
If the user expresses crisis thoughts, acknowledge their pain and suggest immediate professional support.
Limit responses to 2-3 sentences for conversational flow.

User message: {prompt}

Therapeutic response:"""
            
            # Generate response with timeout handling
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Vertex AI request timed out")
            
            # Set timeout for 10 seconds
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                response = self.model.generate_content(therapeutic_prompt)
                signal.alarm(0)  # Cancel timeout
                
                if response and hasattr(response, 'text') and response.text:
                    generated_text = response.text.strip()
                    logger.info(f"Successfully generated Vertex AI response: {len(generated_text)} chars")
                    return generated_text
                else:
                    logger.warning("Empty or invalid response from Vertex AI")
                    raise Exception("Empty response from Vertex AI")
            finally:
                signal.alarm(0)  # Ensure timeout is cancelled
                
        except TimeoutError as e:
            logger.error(f"Vertex AI timeout: {e}")
            raise Exception(f"Vertex AI timeout: {e}")
        except Exception as e:
            logger.error(f"Error generating Vertex AI response: {e}")
            raise Exception(f"Vertex AI error: {e}")
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide safe fallback responses when Vertex AI is unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["help", "support"]):
            return "I'm here to support you. Can you tell me more about what you're experiencing?"
        elif any(word in message_lower for word in ["sad", "depressed", "down"]):
            return "I understand you're feeling sad. These feelings are valid. Would you like to talk about what's contributing to these feelings?"
        elif any(word in message_lower for word in ["anxious", "anxiety", "worried", "stress"]):
            return "Anxiety can feel overwhelming. Let's take this one step at a time. What's been on your mind lately?"
        elif any(word in message_lower for word in ["angry", "frustrated", "mad"]):
            return "It sounds like you're dealing with some intense emotions. Anger often signals that something important to us feels threatened. Can you share more?"
        elif any(word in message_lower for word in ["hurt", "harm", "kill", "die", "suicide"]):
            return "I'm concerned about what you're sharing. Your life has value. Please reach out to a crisis helpline or emergency services immediately. You don't have to go through this alone."
        else:
            return "Thank you for sharing with me. I'm here to listen and support you. Can you tell me more about how you're feeling right now?"

# Global client instance
_vertex_client = None

def get_vertex_client() -> VertexAIClient:
    """Get or create Vertex AI client instance"""
    global _vertex_client
    if _vertex_client is None:
        _vertex_client = VertexAIClient()
    return _vertex_client

def send_to_vertex_ai(message: str) -> str:
    """Send message to Vertex AI and return therapeutic response"""
    client = get_vertex_client()
    return client.generate_response(message)

async def get_ai_response(message: str) -> str:
    """Get AI response with Vertex AI primary and Ollama fallback"""
    use_vertex = os.getenv("USE_VERTEX_AI", "true").lower() == "true"
    
    # Try Vertex AI first if enabled
    if use_vertex:
        try:
            client = get_vertex_client()
            if client.model:  # Vertex AI is properly initialized
                response = client.generate_response(message)
                # Check if we got a real Vertex AI response (not internal fallback)
                if response and len(response) > 50:  # Simple check for substantial response
                    logger.info("Successfully got Vertex AI response")
                    return response
                logger.warning("Vertex AI returned insufficient response, trying Ollama")
        except Exception as e:
            logger.error(f"Vertex AI failed: {e}, trying Ollama fallback")
    else:
        logger.info("Vertex AI disabled, using Ollama")
    
    # Try Ollama fallback
    try:
        from .ollama import get_ollama_response
        response = await get_ollama_response(message)
        logger.info("Successfully got Ollama fallback response")
        return response
    except Exception as e:
        logger.error(f"Ollama fallback failed: {e}")
    
    # Final fallback - raise exception to be handled by endpoint
    logger.error("Both Vertex AI and Ollama failed")
    raise Exception("No AI backend available")