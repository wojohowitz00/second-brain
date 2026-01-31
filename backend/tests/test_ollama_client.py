#!/usr/bin/env python3
"""
Tests for ollama_client module.

TDD approach: Tests written FIRST, implementation follows.
Tests use mocks for unit tests, real Ollama for integration tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from ollama import ResponseError


class TestOllamaHealthCheck:
    """Test cases for health check methods."""
    
    def test_server_not_running_returns_false(self):
        """is_server_running() returns False when server unreachable."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        with patch.object(client.health_client, 'list', side_effect=httpx.ConnectError("Connection refused")):
            assert client.is_server_running() is False
    
    def test_server_running_returns_true(self):
        """is_server_running() returns True when server responds."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        mock_response = Mock()
        mock_response.models = []
        with patch.object(client.health_client, 'list', return_value=mock_response):
            assert client.is_server_running() is True
    
    def test_model_available_exact_match(self):
        """is_model_available() finds exact model name."""
        from ollama_client import OllamaClient
        
        client = OllamaClient(model="llama3.2:3b")
        
        mock_model = Mock()
        mock_model.model = "llama3.2:3b"
        mock_response = Mock()
        mock_response.models = [mock_model]
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            assert client.is_model_available() is True
    
    def test_model_available_prefix_match(self):
        """is_model_available() finds model by prefix."""
        from ollama_client import OllamaClient
        
        client = OllamaClient(model="llama3.2:3b")
        
        mock_model = Mock()
        mock_model.model = "llama3.2:3b-instruct-q4_K_M"
        mock_response = Mock()
        mock_response.models = [mock_model]
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            assert client.is_model_available() is True
    
    def test_model_not_available_returns_false(self):
        """is_model_available() returns False for missing model."""
        from ollama_client import OllamaClient
        
        client = OllamaClient(model="nonexistent-model")
        
        mock_model = Mock()
        mock_model.model = "other-model"
        mock_response = Mock()
        mock_response.models = [mock_model]
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            assert client.is_model_available() is False
    
    def test_health_check_all_ok(self):
        """health_check() returns ready=True when all checks pass."""
        from ollama_client import OllamaClient
        
        client = OllamaClient(model="llama3.2:3b")
        
        mock_model = Mock()
        mock_model.model = "llama3.2:3b"
        mock_response = Mock()
        mock_response.models = [mock_model]
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            status = client.health_check()
            assert status.ready is True
            assert status.server_running is True
            assert status.model_available is True
            assert status.error is None
    
    def test_health_check_server_down(self):
        """health_check() returns error when server not running."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        with patch.object(client.health_client, 'list', side_effect=httpx.ConnectError("Connection refused")):
            status = client.health_check()
            assert status.ready is False
            assert status.server_running is False
            assert "not running" in status.error.lower()
    
    def test_health_check_model_missing(self):
        """health_check() returns error when model not found."""
        from ollama_client import OllamaClient
        
        client = OllamaClient(model="nonexistent-model")
        
        mock_response = Mock()
        mock_response.models = []
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            status = client.health_check()
            assert status.ready is False
            assert status.model_available is False
            assert "not found" in status.error.lower()
    
    def test_list_models_returns_names(self):
        """list_models() returns list of model names."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        mock_model1 = Mock()
        mock_model1.model = "model1"
        mock_model2 = Mock()
        mock_model2.model = "model2"
        mock_response = Mock()
        mock_response.models = [mock_model1, mock_model2]
        
        with patch.object(client.health_client, 'list', return_value=mock_response):
            models = client.list_models()
            assert models == ["model1", "model2"]


class TestOllamaChat:
    """Test cases for chat operations."""
    
    def test_chat_returns_response(self):
        """chat() returns model response."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = "Hello!"
        
        with patch.object(client.client, 'chat', return_value=mock_response):
            response = client.chat([{"role": "user", "content": "Say hello"}])
            assert response["message"]["content"] == "Hello!"
    
    def test_chat_server_not_running_raises(self):
        """chat() raises OllamaServerNotRunning on connection error."""
        from ollama_client import OllamaClient, OllamaServerNotRunning
        
        client = OllamaClient()
        
        with patch.object(client.client, 'chat', side_effect=httpx.ConnectError("Connection refused")):
            with pytest.raises(OllamaServerNotRunning):
                client.chat([{"role": "user", "content": "test"}])
    
    def test_chat_timeout_raises(self):
        """chat() raises OllamaTimeout on timeout."""
        from ollama_client import OllamaClient, OllamaTimeout
        
        client = OllamaClient()
        
        with patch.object(client.client, 'chat', side_effect=httpx.TimeoutException("Request timed out")):
            with pytest.raises(OllamaTimeout):
                client.chat([{"role": "user", "content": "test"}])
    
    def test_chat_model_not_found_raises(self):
        """chat() raises OllamaModelNotFound on 404."""
        from ollama_client import OllamaClient, OllamaModelNotFound
        
        client = OllamaClient()
        
        error = ResponseError("model not found", status_code=404)
        with patch.object(client.client, 'chat', side_effect=error):
            with pytest.raises(OllamaModelNotFound):
                client.chat([{"role": "user", "content": "test"}])


class TestOllamaGenerate:
    """Test cases for generate operations."""
    
    def test_generate_returns_response(self):
        """generate() returns generated text."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        mock_response = Mock()
        mock_response.response = "Generated text"
        
        with patch.object(client.client, 'generate', return_value=mock_response):
            response = client.generate("test prompt")
            assert response["response"] == "Generated text"
    
    def test_generate_server_not_running_raises(self):
        """generate() raises OllamaServerNotRunning on connection error."""
        from ollama_client import OllamaClient, OllamaServerNotRunning
        
        client = OllamaClient()
        
        with patch.object(client.client, 'generate', side_effect=httpx.ConnectError("Connection refused")):
            with pytest.raises(OllamaServerNotRunning):
                client.generate("test")


class TestOllamaVerify:
    """Test cases for model verification."""
    
    def test_verify_model_responds_success(self):
        """verify_model_responds() returns True when model responds."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        mock_response = Mock()
        mock_response.response = "OK"
        
        with patch.object(client.client, 'generate', return_value=mock_response):
            assert client.verify_model_responds() is True
    
    def test_verify_model_responds_failure(self):
        """verify_model_responds() returns False on error."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        
        with patch.object(client.client, 'generate', side_effect=Exception("Error")):
            assert client.verify_model_responds() is False


# Integration tests (require real Ollama)
@pytest.mark.integration
class TestOllamaIntegration:
    """Integration tests with real Ollama server."""
    
    def test_real_health_check(self):
        """Test health check against real Ollama server."""
        from ollama_client import OllamaClient
        
        client = OllamaClient()
        status = client.health_check()
        
        # Should return a status (may be ready or not, depending on setup)
        assert hasattr(status, 'ready')
        assert hasattr(status, 'server_running')
        assert hasattr(status, 'model_available')
    
    def test_real_chat_response(self):
        """Test chat with real Ollama server."""
        from ollama_client import OllamaClient, OllamaModelNotFound
        
        client = OllamaClient()
        status = client.health_check()
        
        if not status.ready:
            pytest.skip(f"Ollama not ready: {status.error}")
        
        try:
            response = client.chat([{"role": "user", "content": "Say hello"}])
            assert "message" in response
            assert "content" in response["message"]
        except OllamaModelNotFound:
            pytest.skip("Model not available - run: ollama pull llama3.2:3b")
