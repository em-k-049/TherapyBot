import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.vertex_ai import VertexAIClient, send_to_vertex_ai, get_ai_response
import os

class TestVertexAIClient:
    
    @patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project", "GCP_REGION": "us-central1"})
    @patch("app.services.vertex_ai.vertexai")
    @patch("app.services.vertex_ai.GenerativeModel")
    def test_initialization_success(self, mock_model_class, mock_vertexai):
        """Test successful Vertex AI client initialization"""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        client = VertexAIClient()
        
        assert client.project_id == "test-project"
        assert client.region == "us-central1"
        assert client.model_name == "gemini-2.0-flash-exp"
        mock_vertexai.init.assert_called_once_with(project="test-project", location="us-central1")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_missing_project_id(self):
        """Test initialization fails without project ID"""
        client = VertexAIClient()
        assert client.model is None
    
    @patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"})
    @patch("app.services.vertex_ai.vertexai")
    @patch("app.services.vertex_ai.GenerativeModel")
    def test_generate_response_success(self, mock_model_class, mock_vertexai):
        """Test successful response generation"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "I understand you're feeling anxious. Let's work through this together."
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        client = VertexAIClient()
        response = client.generate_response("I'm feeling anxious")
        
        assert response == "I understand you're feeling anxious. Let's work through this together."
        mock_model.generate_content.assert_called_once()
    
    @patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"})
    @patch("app.services.vertex_ai.vertexai")
    @patch("app.services.vertex_ai.GenerativeModel")
    def test_generate_response_empty_response(self, mock_model_class, mock_vertexai):
        """Test handling of empty response from Vertex AI"""
        mock_response = Mock()
        mock_response.text = ""
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        client = VertexAIClient()
        response = client.generate_response("I'm feeling sad")
        
        # Should return fallback response
        assert "sad" in response.lower() or "feeling" in response.lower()
    
    @patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"})
    @patch("app.services.vertex_ai.vertexai")
    @patch("app.services.vertex_ai.GenerativeModel")
    def test_generate_response_api_error(self, mock_model_class, mock_vertexai):
        """Test handling of API errors"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        client = VertexAIClient()
        response = client.generate_response("Hello")
        
        # Should return fallback response
        assert "support" in response.lower() or "feeling" in response.lower()
    
    def test_fallback_responses(self):
        """Test fallback response patterns"""
        client = VertexAIClient()
        client.model = None  # Force fallback mode
        
        # Test different emotional states
        sad_response = client.generate_response("I'm feeling very sad")
        assert "sad" in sad_response.lower()
        
        anxiety_response = client.generate_response("I'm anxious about everything")
        assert "anxiety" in anxiety_response.lower() or "anxious" in anxiety_response.lower()
        
        anger_response = client.generate_response("I'm so angry and frustrated")
        assert "anger" in anger_response.lower() or "emotions" in anger_response.lower()
        
        crisis_response = client.generate_response("I want to hurt myself")
        assert "crisis" in crisis_response.lower() or "emergency" in crisis_response.lower()
    
    @patch("app.services.vertex_ai.get_vertex_client")
    def test_send_to_vertex_ai(self, mock_get_client):
        """Test send_to_vertex_ai function"""
        mock_client = Mock()
        mock_client.generate_response.return_value = "Test response"
        mock_get_client.return_value = mock_client
        
        response = send_to_vertex_ai("Test message")
        
        assert response == "Test response"
        mock_client.generate_response.assert_called_once_with("Test message")
    
    @pytest.mark.asyncio
    @patch("app.services.vertex_ai.send_to_vertex_ai")
    async def test_get_ai_response_async(self, mock_send):
        """Test async wrapper function"""
        mock_send.return_value = "Async test response"
        
        response = await get_ai_response("Async test message")
        
        assert response == "Async test response"
        mock_send.assert_called_once_with("Async test message")

class TestVertexAIIntegration:
    """Integration tests for Vertex AI service"""
    
    @patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"})
    @patch("app.services.vertex_ai.vertexai")
    @patch("app.services.vertex_ai.GenerativeModel")
    def test_therapeutic_prompt_structure(self, mock_model_class, mock_vertexai):
        """Test that therapeutic context is properly added to prompts"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Therapeutic response")
        mock_model_class.return_value = mock_model
        
        client = VertexAIClient()
        client.generate_response("I need help")
        
        # Verify the prompt includes therapeutic context
        call_args = mock_model.generate_content.call_args[0][0]
        assert "compassionate AI therapist" in call_args
        assert "empathy" in call_args
        assert "I need help" in call_args
    
    def test_crisis_detection_in_fallback(self):
        """Test crisis keyword detection in fallback responses"""
        client = VertexAIClient()
        client.model = None
        
        crisis_keywords = ["hurt myself", "kill myself", "want to die", "suicide"]
        
        for keyword in crisis_keywords:
            response = client.generate_response(f"I want to {keyword}")
            assert any(word in response.lower() for word in ["crisis", "emergency", "helpline", "value"])