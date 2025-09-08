import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    with patch('app.services.ai_service.get_ai_service') as mock:
        service = AsyncMock()
        service.get_response.return_value = "I understand you're feeling anxious. Let's work through this together."
        mock.return_value = service
        yield service

@pytest.fixture
def mock_auth():
    """Mock authentication for testing"""
    with patch('app.deps.get_current_user') as mock:
        mock.return_value = type('User', (), {'id': 1, 'role': type('Role', (), {'name': 'patient'})})()
        yield mock

class TestChatEndpoints:
    
    def test_test_chat_success(self, mock_ai_service):
        """Test /messages/test-chat success"""
        response = client.post(
            "/messages/test-chat",
            json={"message": "Hello, how are you?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ai_response" in data
        assert data["status"] == "success"
        assert data["user_message"] == "Hello, how are you?"
    
    def test_test_chat_ai_failure(self):
        """Test /messages/test-chat when AI fails"""
        with patch('app.services.ai_service.get_ai_service') as mock:
            service = AsyncMock()
            service.get_response.side_effect = Exception("AI service down")
            mock.return_value = service
            
            response = client.post(
                "/messages/test-chat",
                json={"message": "Hello"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert data["status"] == "error"
            assert "technical difficulties" in data["ai_response"]
    
    def test_test_chat_invalid_payload(self):
        """Test /messages/test-chat with invalid payload"""
        response = client.post(
            "/messages/test-chat",
            json={}
        )
        assert response.status_code == 422
    
    def test_chat_success(self, mock_ai_service, mock_auth):
        """Test /messages/chat success"""
        response = client.post(
            "/messages/chat",
            json={"message": "I'm feeling anxious"},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ai_response" in data
        assert data["user_message"] == "I'm feeling anxious"
    
    def test_chat_no_auth(self):
        """Test /messages/chat without authentication"""
        response = client.post(
            "/messages/chat",
            json={"message": "Hello"}
        )
        assert response.status_code == 401
    
    def test_voice_chat_success(self, mock_ai_service, mock_auth):
        """Test /messages/voice-chat success"""
        response = client.post(
            "/messages/voice-chat",
            json={"message": "I need help", "return_audio": True},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ai_response" in data
        assert data["user_message"] == "I need help"
    
    def test_voice_chat_missing_message(self, mock_auth):
        """Test /messages/voice-chat with missing message"""
        response = client.post(
            "/messages/voice-chat",
            json={"return_audio": True},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 400

class TestHealthEndpoint:
    
    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestErrorHandling:
    
    def test_malformed_json(self):
        """Test malformed JSON handling"""
        response = client.post(
            "/messages/test-chat",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test missing content type"""
        response = client.post(
            "/messages/test-chat",
            data='{"message": "test"}'
        )
        assert response.status_code == 422