# Phase 3: Ollama Connection - Research

**Researched:** 2026-01-31
**Domain:** Local LLM integration, Ollama API, health checks, error handling
**Confidence:** HIGH

## Summary

Phase 3 requires establishing a reliable connection to a local Ollama instance for LLM-powered classification. This is a **CRITICAL CHECKPOINT** - the quality of local classification must be validated before investing in UI/packaging phases.

The Ollama Python library (`pip install ollama`) provides a clean API for all required operations: health checks, model listing, model loading, and chat/generate completions. The library wraps the Ollama REST API (`http://localhost:11434`) and handles streaming, error responses, and timeouts.

**Primary recommendation:** Use the official `ollama` Python package with a custom client configured for appropriate timeouts (30s default, configurable). Implement a health check module that verifies: (1) Ollama server is running, (2) required model is available, (3) model can generate responses. Use the `Client` class for synchronous operations (simpler for this use case) and wrap all calls in try/except for graceful error handling.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ollama | >=0.4.0 | Official Ollama Python client | Maintained by Ollama team, covers all API operations |
| httpx | (via ollama) | HTTP client | Ollama library dependency, handles connections |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typing | stdlib | Type hints for responses | Improves IDE support |
| dataclasses | stdlib | Response DTOs | Clean data structures |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ollama library | Raw httpx/requests | More control but lose type safety, error handling, streaming support |
| ollama library | langchain | Heavy dependency, unnecessary abstraction for direct Ollama use |
| ollama library | litellm | Multi-provider library, overkill for Ollama-only use case |
| Sync Client | AsyncClient | Async adds complexity; sync sufficient for sequential classification |

**Installation:**
```bash
uv add ollama
# or
pip install ollama
```

## Architecture Patterns

### Recommended Project Structure
```
backend/_scripts/
├── ollama_client.py    # Ollama connection module (new)
├── vault_scanner.py    # Existing scanner (Phase 2)
├── state.py            # Existing state management
└── .state/
    └── [existing state files]
```

### Pattern 1: Health Check with Graceful Degradation

**What:** Check if Ollama is running before attempting operations.

**When to use:** On startup, before any LLM operation, periodically during runtime.

**Example:**
```python
from ollama import Client
from ollama import ResponseError
import httpx

class OllamaHealthChecker:
    """Check Ollama server and model availability."""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: float = 10.0):
        self.host = host
        self.timeout = timeout
        self._client = None
    
    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(host=self.host, timeout=self.timeout)
        return self._client
    
    def is_server_running(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            # list() hits /api/tags - lightweight health check
            self.client.list()
            return True
        except httpx.ConnectError:
            return False
        except httpx.TimeoutException:
            return False
        except Exception:
            return False
    
    def is_model_available(self, model: str) -> bool:
        """Check if specific model is downloaded."""
        try:
            models = self.client.list()
            model_names = [m.model for m in models.models]
            # Handle both "llama3.2:3b" and "llama3.2:3b-instruct" formats
            return any(model in name or name.startswith(model) for name in model_names)
        except Exception:
            return False
    
    def get_health_status(self, required_model: str) -> dict:
        """Get comprehensive health status."""
        status = {
            "server_running": False,
            "model_available": False,
            "model_name": required_model,
            "ready": False,
            "error": None
        }
        
        if not self.is_server_running():
            status["error"] = "Ollama server not running"
            return status
        
        status["server_running"] = True
        
        if not self.is_model_available(required_model):
            status["error"] = f"Model '{required_model}' not found. Run: ollama pull {required_model}"
            return status
        
        status["model_available"] = True
        status["ready"] = True
        return status
```

### Pattern 2: Client with Configurable Timeout

**What:** Create Ollama client with appropriate timeout for LLM operations.

**When to use:** LLM operations can take 5-30+ seconds, especially on cold start.

**Example:**
```python
from ollama import Client
from typing import Optional
import os

# Configuration
DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_TIMEOUT = 30.0  # seconds - generous for cold start
WARM_TIMEOUT = 10.0     # seconds - model already loaded

class OllamaClientManager:
    """Manage Ollama client lifecycle and configuration."""
    
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT
    ):
        self.host = os.environ.get("OLLAMA_HOST", host)
        self.model = os.environ.get("OLLAMA_MODEL", model)
        self.timeout = timeout
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Lazy-initialize client."""
        if self._client is None:
            self._client = Client(
                host=self.host,
                timeout=self.timeout
            )
        return self._client
    
    def chat(self, messages: list[dict], stream: bool = False) -> dict:
        """Send chat messages to model."""
        return self.client.chat(
            model=self.model,
            messages=messages,
            stream=stream
        )
    
    def generate(self, prompt: str, stream: bool = False) -> dict:
        """Generate completion from prompt."""
        return self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=stream
        )
```

### Pattern 3: Error Handling with Specific Exception Types

**What:** Handle different error conditions appropriately.

**When to use:** All Ollama operations should be wrapped in error handling.

**Example:**
```python
from ollama import Client, ResponseError
import httpx

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

def safe_chat(client: Client, model: str, messages: list[dict]) -> dict:
    """
    Execute chat with comprehensive error handling.
    
    Raises:
        OllamaServerNotRunning: Server not reachable
        OllamaModelNotFound: Model not downloaded
        OllamaTimeout: Request timed out
        OllamaError: Other errors
    """
    try:
        return client.chat(model=model, messages=messages)
    
    except httpx.ConnectError as e:
        raise OllamaServerNotRunning(
            "Ollama server not running. Start with: ollama serve"
        ) from e
    
    except httpx.TimeoutException as e:
        raise OllamaTimeout(
            f"Request timed out after {client._client.timeout}s. "
            "Model may be loading or system under heavy load."
        ) from e
    
    except ResponseError as e:
        if e.status_code == 404:
            raise OllamaModelNotFound(
                f"Model '{model}' not found. Run: ollama pull {model}"
            ) from e
        raise OllamaError(f"Ollama API error: {e.error}") from e
    
    except Exception as e:
        raise OllamaError(f"Unexpected error: {e}") from e
```

### Pattern 4: Model Loading Verification

**What:** Verify model can generate responses before relying on it.

**When to use:** After health check passes, verify end-to-end functionality.

**Example:**
```python
def verify_model_responds(client: Client, model: str, timeout: float = 30.0) -> bool:
    """
    Verify model can generate a response.
    
    Uses a simple prompt to minimize latency.
    Returns True if model responds, False on any error.
    """
    test_prompt = "Respond with exactly: OK"
    
    try:
        response = client.generate(
            model=model,
            prompt=test_prompt,
            options={"num_predict": 10}  # Limit output tokens
        )
        # Check we got some response
        return bool(response.get("response", "").strip())
    except Exception:
        return False
```

### Anti-Patterns to Avoid

- **No timeout configuration:** Default httpx timeout may be too short for LLM inference. Always configure explicit timeout.
- **Assuming Ollama is always running:** Server may crash, restart, or not be started. Always check before operations.
- **Not handling cold start:** First request after model load takes 10-30s. Subsequent requests are faster.
- **Ignoring model availability:** Model may not be downloaded. Check with `client.list()` before `client.chat()`.
- **Using async when not needed:** AsyncClient adds complexity. Sync is fine for sequential classification.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP client with retries | Custom requests wrapper | ollama library | Already handles retries, connection pooling |
| Response parsing | Manual JSON parsing | ollama library types | Typed responses with proper validation |
| Streaming handling | Manual chunk processing | ollama library iterator | Built-in streaming support |
| Model name validation | String matching | `client.list()` | Authoritative list from server |

## Common Pitfalls

### Pitfall 1: Cold Start Timeout

**What goes wrong:** First request after model load times out at default 10s.

**Why it happens:** Ollama loads model into memory on first request. Llama 3.2 3B takes 10-20s to load on M1/M2 Mac.

**How to avoid:**
- Set timeout to 30s minimum for initial requests
- Consider a "warm-up" request on startup
- Document expected latency for users

**Warning signs:** Consistent timeout on first request, success on retry.

### Pitfall 2: Model Name Mismatch

**What goes wrong:** `ResponseError 404` when model exists in library.

**Why it happens:** Model names include tags. "llama3.2:3b" vs "llama3.2:3b-instruct-q4_K_M" are different.

**How to avoid:**
- Use `client.list()` to get exact model names
- Match model name prefix rather than exact string
- Document the specific model tag required

**Warning signs:** Model shows in `ollama list` but API returns 404.

### Pitfall 3: Server Not Running on macOS

**What goes wrong:** `httpx.ConnectError` even though Ollama is "installed".

**Why it happens:** Ollama.app must be running (menu bar icon), or `ollama serve` must be active.

**How to avoid:**
- Check server status before any operation
- Provide clear error message with startup instructions
- Consider auto-launching Ollama.app (Phase 8)

**Warning signs:** All operations fail with connection refused.

### Pitfall 4: Insufficient VRAM/RAM

**What goes wrong:** Model loads but generates garbage or crashes.

**Why it happens:** Model doesn't fit in memory, causing swapping or partial loading.

**How to avoid:**
- Llama 3.2 3B needs ~4GB RAM minimum
- Document system requirements
- Detect via slow response times (>60s)

**Warning signs:** Very slow responses, garbled output, system memory warnings.

## Code Examples

### Complete Ollama Client Module

```python
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
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_TIMEOUT = 30.0  # Cold start can take 20s+
HEALTH_CHECK_TIMEOUT = 5.0


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
    
    def chat(self, messages: list[dict], stream: bool = False) -> dict:
        """
        Send chat messages to model.
        
        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."}
            stream: If True, return iterator for streaming responses
            
        Returns:
            Response dict with "message" containing model's reply.
            
        Raises:
            OllamaServerNotRunning: Server not reachable
            OllamaModelNotFound: Model not downloaded
            OllamaTimeout: Request timed out
            OllamaError: Other errors
        """
        try:
            return self.client.chat(
                model=self.model,
                messages=messages,
                stream=stream
            )
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
            return self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=stream
            )
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
            return bool(response.get("response", "").strip())
        except Exception:
            return False


# Convenience functions
def get_ollama_client() -> OllamaClient:
    """Get configured Ollama client."""
    return OllamaClient()


def check_ollama_health() -> HealthStatus:
    """Quick health check of Ollama."""
    return OllamaClient().health_check()
```

### Test Module Structure

```python
#!/usr/bin/env python3
"""
Tests for Ollama client module.

TDD approach: Tests written FIRST, implementation follows.
"""

import pytest
from unittest.mock import Mock, patch

# Tests for health check
class TestOllamaHealthCheck:
    
    def test_server_not_running_returns_false(self):
        """is_server_running() returns False when server unreachable."""
        pass
    
    def test_server_running_returns_true(self):
        """is_server_running() returns True when server responds."""
        pass
    
    def test_model_available_when_exact_match(self):
        """is_model_available() finds exact model name."""
        pass
    
    def test_model_available_when_prefix_match(self):
        """is_model_available() finds model by prefix."""
        pass
    
    def test_model_not_available_returns_false(self):
        """is_model_available() returns False for missing model."""
        pass
    
    def test_health_check_all_ok(self):
        """health_check() returns ready=True when all checks pass."""
        pass
    
    def test_health_check_server_down(self):
        """health_check() returns error when server not running."""
        pass
    
    def test_health_check_model_missing(self):
        """health_check() returns error when model not found."""
        pass


# Tests for chat/generate
class TestOllamaChat:
    
    def test_chat_returns_response(self):
        """chat() returns model response."""
        pass
    
    def test_chat_server_not_running_raises(self):
        """chat() raises OllamaServerNotRunning on connection error."""
        pass
    
    def test_chat_timeout_raises(self):
        """chat() raises OllamaTimeout on timeout."""
        pass
    
    def test_chat_model_not_found_raises(self):
        """chat() raises OllamaModelNotFound on 404."""
        pass


# Tests for generate
class TestOllamaGenerate:
    
    def test_generate_returns_response(self):
        """generate() returns generated text."""
        pass
    
    def test_generate_server_not_running_raises(self):
        """generate() raises OllamaServerNotRunning on connection error."""
        pass


# Integration tests (require real Ollama)
@pytest.mark.integration
class TestOllamaIntegration:
    
    def test_real_health_check(self):
        """Test health check against real Ollama server."""
        pass
    
    def test_real_chat_response(self):
        """Test chat with real Ollama server."""
        pass
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Raw REST API calls | Official Python library | 2024 | Type safety, error handling, streaming |
| requests library | httpx (via ollama) | 2023 | Async support, HTTP/2, better timeouts |
| No health checks | Pre-operation health validation | Best practice | Graceful degradation, clear errors |
| Fixed timeouts | Configurable per-operation | Best practice | Cold start handling |

**Deprecated/outdated:**
- **Manual JSON parsing:** Use ollama library's typed responses
- **Global timeout settings:** Configure per-client based on operation type
- **Ignoring cold start:** Always account for model loading latency

## Open Questions

1. **Which Llama 3.2 variant to use?**
   - What we know: "llama3.2:3b" is specified in ROADMAP
   - What's unclear: Instruct variant (`llama3.2:3b-instruct`) better for classification?
   - Recommendation: Test both in Phase 4, document performance difference

2. **Should we auto-pull missing models?**
   - What we know: `ollama pull` downloads models (~2GB for 3B)
   - What's unclear: Auto-pull in Phase 3, or defer to Phase 8 wizard?
   - Recommendation: Defer auto-pull to Phase 8. Phase 3 should error clearly and document manual steps.

3. **How to handle Ollama.app vs ollama serve?**
   - What we know: macOS users typically run Ollama.app (menu bar), Linux uses `ollama serve`
   - What's unclear: Should we detect which mode, or treat them identically?
   - Recommendation: Treat identically - both expose same API on same port. Document both startup methods.

## Sources

### Primary (HIGH confidence)
- [Ollama Python Library README](https://github.com/ollama/ollama-python) - Official documentation
- [Ollama API Documentation](https://docs.ollama.com/api) - REST API reference
- [Ollama Health Check Endpoints](https://docs.ollama.com/api/ps) - Health check patterns

### Secondary (MEDIUM confidence)
- [Timeout issues discussion](https://github.com/ollama/ollama-python/issues/218) - Community patterns
- [Connection error handling](https://github.com/ollama/ollama/issues/8214) - Error scenarios

### Tertiary (LOW confidence)
- Stack Overflow discussions on async patterns
- Blog posts on LLM integration patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official library, well-documented
- Architecture: HIGH - Common patterns, verified against library source
- Pitfalls: HIGH - Documented issues, community-validated

**Research date:** 2026-01-31
**Valid until:** 2026-04-01 (90 days - Ollama API stable, library actively maintained)
