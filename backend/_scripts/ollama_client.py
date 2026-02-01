#!/usr/bin/env python3
"""
Ollama client for local LLM classification.

Provides health checks, model verification, and chat/generate operations
with comprehensive error handling.
"""

from dataclasses import dataclass
from typing import Optional
import os

from ollama import Client, ResponseError
import httpx


# Configuration
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:latest"
DEFAULT_TIMEOUT = 30.0  # Cold start can take 20s+
HEALTH_CHECK_TIMEOUT = 5.0  # Quick health checks


# Custom exceptions
class OllamaError(Exception):
    """Base exception for Ollama operations."""
    pass


class OllamaServerNotRunning(OllamaError):
    """Ollama server is not running."""
    pass


class OllamaModelNotFound(OllamaError):
    """Requested model is not available."""
    pass


class OllamaTimeout(OllamaError):
    """Operation timed out."""
    pass


@dataclass
class HealthStatus:
    """Ollama health check result."""
    server_running: bool
    model_available: bool
    model_name: str
    ready: bool
    error: Optional[str] = None


class OllamaClient:
    """
    Client for interacting with local Ollama instance.
    
    Usage:
        client = OllamaClient()
        
        # Check health before use
        status = client.health_check()
        if not status.ready:
            print(f"Error: {status.error}")
            return
        
        # Send chat message
        response = client.chat([
            {"role": "user", "content": "Classify: Meeting notes from project sync"}
        ])
        print(response["message"]["content"])
    """
    
    def __init__(
        self,
        host: str = None,
        model: str = None,
        timeout: float = DEFAULT_TIMEOUT
    ):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama server URL (default: http://localhost:11434)
            model: Model to use for chat/generate (default: llama3.2:3b)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.host = host or os.environ.get("OLLAMA_HOST", DEFAULT_HOST)
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self.timeout = timeout
        self._client: Optional[Client] = None
        self._health_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get client for LLM operations (longer timeout)."""
        if self._client is None:
            self._client = Client(host=self.host, timeout=self.timeout)
        return self._client
    
    @property
    def health_client(self) -> Client:
        """Get client for health checks (shorter timeout)."""
        if self._health_client is None:
            self._health_client = Client(host=self.host, timeout=HEALTH_CHECK_TIMEOUT)
        return self._health_client
    
    def is_server_running(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            self.health_client.list()
            return True
        except (httpx.ConnectError, httpx.TimeoutException):
            return False
        except Exception:
            return False
    
    def is_model_available(self) -> bool:
        """Check if configured model is available."""
        try:
            models = self.health_client.list()
            model_names = [m.model for m in models.models]
            return any(
                self.model in name or name.startswith(self.model.split(":")[0])
                for name in model_names
            )
        except Exception:
            return False
    
    def list_models(self) -> list[str]:
        """Get list of available model names."""
        try:
            models = self.health_client.list()
            return [m.model for m in models.models]
        except Exception:
            return []
    
    def health_check(self) -> HealthStatus:
        """
        Perform comprehensive health check.
        
        Returns:
            HealthStatus with server/model availability and any errors.
        """
        status = HealthStatus(
            server_running=False,
            model_available=False,
            model_name=self.model,
            ready=False,
            error=None
        )
        
        if not self.is_server_running():
            status.error = "Ollama server not running. Start with: ollama serve"
            return status
        
        status.server_running = True
        
        if not self.is_model_available():
            status.error = f"Model '{self.model}' not found. Run: ollama pull {self.model}"
            return status
        
        status.model_available = True
        status.ready = True
        return status
    
    def chat(self, messages: list[dict], stream: bool = False, model: Optional[str] = None) -> dict:
        """
        Send chat messages to model.

        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            stream: If True, return iterator for streaming responses
            model: Override model for this call (default: use instance model)

        Returns:
            Response dict with "message" containing model's reply.
            
        Raises:
            OllamaServerNotRunning: Server not reachable
            OllamaModelNotFound: Model not downloaded
            OllamaTimeout: Request timed out
            OllamaError: Other errors
        """
        try:
            response = self.client.chat(
                model=model or self.model,
                messages=messages,
                stream=stream
            )
            # Convert response object to dict for consistency
            if hasattr(response, 'message'):
                return {
                    "message": {
                        "content": response.message.content,
                        "role": getattr(response.message, 'role', 'assistant')
                    }
                }
            return response
        except httpx.ConnectError as e:
            raise OllamaServerNotRunning(
                "Ollama server not running. Start with: ollama serve"
            ) from e
        except httpx.TimeoutException as e:
            raise OllamaTimeout(
                f"Request timed out after {self.timeout}s. "
                "Model may be loading (cold start takes 10-30s)."
            ) from e
        except ResponseError as e:
            if e.status_code == 404:
                raise OllamaModelNotFound(
                    f"Model '{self.model}' not found. Run: ollama pull {self.model}"
                ) from e
            raise OllamaError(f"Ollama API error: {e.error}") from e
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}") from e
    
    def generate(self, prompt: str, stream: bool = False) -> dict:
        """
        Generate completion from prompt.
        
        Args:
            prompt: Input prompt string
            stream: If True, return iterator for streaming responses
            
        Returns:
            Response dict with "response" containing generated text.
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=stream
            )
            # Convert response object to dict for consistency
            if hasattr(response, 'response'):
                return {"response": response.response}
            return response
        except httpx.ConnectError as e:
            raise OllamaServerNotRunning(
                "Ollama server not running. Start with: ollama serve"
            ) from e
        except httpx.TimeoutException as e:
            raise OllamaTimeout(
                f"Request timed out after {self.timeout}s."
            ) from e
        except ResponseError as e:
            if e.status_code == 404:
                raise OllamaModelNotFound(
                    f"Model '{self.model}' not found. Run: ollama pull {self.model}"
                ) from e
            raise OllamaError(f"Ollama API error: {e.error}") from e
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}") from e
    
    def verify_model_responds(self) -> bool:
        """
        Verify model can generate a response.
        
        Uses a minimal prompt to test end-to-end functionality.
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt="Respond with: OK",
                options={"num_predict": 5}
            )
            return bool(response.get("response", "") if isinstance(response, dict) else getattr(response, 'response', ''))
        except Exception:
            return False


# Convenience functions
def get_ollama_client() -> OllamaClient:
    """Get configured Ollama client."""
    return OllamaClient()


def check_ollama_health() -> HealthStatus:
    """Quick health check of Ollama."""
    return OllamaClient().health_check()
