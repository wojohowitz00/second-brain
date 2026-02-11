#!/usr/bin/env python3
"""
Unified LLM Provider Interface

Supports multiple LLM providers:
- Local: Ollama, LM Studio
- Cloud: Anthropic Claude, OpenAI

Usage:
    from llm_provider import get_provider
    
    provider = get_provider("anthropic", api_key="sk-...")
    result = provider.classify("Some text to classify")
"""

import os
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def classify(self, thought: str) -> Dict[str, Any]:
        """Classify a thought and return structured JSON."""
        pass
    
    @abstractmethod
    def generate_digest(self, context: Dict[str, Any]) -> str:
        """Generate a daily digest from context."""
        pass
    
    @abstractmethod
    def generate_review(self, context: Dict[str, Any]) -> str:
        """Generate a weekly review from context."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def _call_api(self, prompt: str, max_tokens: int = 1024) -> str:
        """Make API call and extract text response."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
    
    def classify(self, thought: str) -> Dict[str, Any]:
        """Classify a thought using Claude."""
        prompt = f"""You are a classifier for a personal knowledge system.

INPUT: {thought}

OUTPUT: Return ONLY valid JSON:
{{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {{
    // For people: name, aliases[] (nicknames), context, follow_ups[]
    // For projects: name, status, next_action, notes
    // For ideas: title, oneliner
    // For admin: task, due_date (if mentioned), status
  }},
  "linked_entities": [
    // People and projects mentioned in the text that should be linked
    {{"name": "Person Name", "type": "person"}},
    {{"name": "Project Name", "type": "project"}}
  ]
}}

RULES:
- "people": Mentions a specific person or follow-up with someone
- "projects": Multi-step work with a next action
- "ideas": Insights, possibilities, explorations
- "admin": One-off tasks, errands
- Always extract concrete next_action for projects (verb + object)
- If confidence < 0.6, still classify but it will be flagged for review
- Extract ALL people and project names mentioned for linked_entities
- Include the primary subject in linked_entities if it's a person/project"""
        
        response_text = self._call_api(prompt)
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        return json.loads(response_text)
    
    def generate_digest(self, context: Dict[str, Any]) -> str:
        """Generate daily digest."""
        prompt = f"""Generate a daily digest under 150 words.

Active projects:
{json.dumps(context.get('projects', []), indent=2)}

People with follow-ups:
{json.dumps(context.get('people', []), indent=2)}

Stalled item (if any):
{json.dumps(context.get('stalled', {}), indent=2)}

Structure:
1. **Top 3 actions for today** (concrete next actions from projects)
2. **One thing you might be avoiding** (oldest or most stalled item)
3. **People follow-ups** (if any are time-sensitive)

Keep it scannable on a phone screen."""
        
        return self._call_api(prompt, max_tokens=500)
    
    def generate_review(self, context: Dict[str, Any]) -> str:
        """Generate weekly review."""
        prompt = f"""Generate a weekly review under 250 words.

Items captured this week:
{json.dumps(context.get('stats', {}), indent=2)}

Active projects:
{json.dumps(context.get('projects', []), indent=2)}

Structure:
1. **What you captured** (breakdown by type)
2. **Progress made** (projects moved forward)
3. **What's stuck** (projects with no recent activity)
4. **One insight** (pattern or theme from the week)

Keep it reflective and actionable."""
        
        return self._call_api(prompt, max_tokens=600)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    def _call_api(self, prompt: str, max_tokens: int = 1024) -> str:
        """Make API call and extract text response."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def classify(self, thought: str) -> Dict[str, Any]:
        """Classify a thought using OpenAI."""
        prompt = f"""You are a classifier for a personal knowledge system.

INPUT: {thought}

OUTPUT: Return ONLY valid JSON:
{{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {{
    // For people: name, aliases[] (nicknames), context, follow_ups[]
    // For projects: name, status, next_action, notes
    // For ideas: title, oneliner
    // For admin: task, due_date (if mentioned), status
  }},
  "linked_entities": [
    // People and projects mentioned in the text that should be linked
    {{"name": "Person Name", "type": "person"}},
    {{"name": "Project Name", "type": "project"}}
  ]
}}

RULES:
- "people": Mentions a specific person or follow-up with someone
- "projects": Multi-step work with a next action
- "ideas": Insights, possibilities, explorations
- "admin": One-off tasks, errands
- Always extract concrete next_action for projects (verb + object)
- If confidence < 0.6, still classify but it will be flagged for review
- Extract ALL people and project names mentioned for linked_entities
- Include the primary subject in linked_entities if it's a person/project"""
        
        response_text = self._call_api(prompt)
        
        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        return json.loads(response_text)
    
    def generate_digest(self, context: Dict[str, Any]) -> str:
        """Generate daily digest."""
        prompt = f"""Generate a daily digest under 150 words.

Active projects:
{json.dumps(context.get('projects', []), indent=2)}

People with follow-ups:
{json.dumps(context.get('people', []), indent=2)}

Stalled item (if any):
{json.dumps(context.get('stalled', {}), indent=2)}

Structure:
1. **Top 3 actions for today** (concrete next actions from projects)
2. **One thing you might be avoiding** (oldest or most stalled item)
3. **People follow-ups** (if any are time-sensitive)

Keep it scannable on a phone screen."""
        
        return self._call_api(prompt, max_tokens=500)
    
    def generate_review(self, context: Dict[str, Any]) -> str:
        """Generate weekly review."""
        prompt = f"""Generate a weekly review under 250 words.

Items captured this week:
{json.dumps(context.get('stats', {}), indent=2)}

Active projects:
{json.dumps(context.get('projects', []), indent=2)}

Structure:
1. **What you captured** (breakdown by type)
2. **Progress made** (projects moved forward)
3. **What's stuck** (projects with no recent activity)
4. **One insight** (pattern or theme from the week)

Keep it reflective and actionable."""
        
        return self._call_api(prompt, max_tokens=600)


class OllamaProvider(LLMProvider):
    """Ollama local provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip("/")
        self.model = model
    
    def _call_api(self, prompt: str) -> str:
        """Make API call to Ollama."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def classify(self, thought: str) -> Dict[str, Any]:
        """Classify a thought using Ollama."""
        prompt = f"""Classify this thought into one of: people, projects, ideas, or admin.

Thought: {thought}

Return ONLY valid JSON:
{{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {{}},
  "linked_entities": []
}}"""
        
        response_text = self._call_api(prompt)
        
        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end].strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "destination": "ideas",
                "confidence": 0.5,
                "filename": thought[:30].lower().replace(" ", "-"),
                "extracted": {},
                "linked_entities": []
            }
    
    def generate_digest(self, context: Dict[str, Any]) -> str:
        """Generate daily digest."""
        prompt = f"""Generate a daily digest under 150 words.

Active projects: {len(context.get('projects', []))}
People with follow-ups: {len(context.get('people', []))}

Structure:
1. Top 3 actions for today
2. One thing you might be avoiding
3. People follow-ups

Keep it scannable."""
        
        return self._call_api(prompt)
    
    def generate_review(self, context: Dict[str, Any]) -> str:
        """Generate weekly review."""
        prompt = f"""Generate a weekly review under 250 words.

Items captured: {json.dumps(context.get('stats', {}))}
Active projects: {len(context.get('projects', []))}

Structure:
1. What you captured
2. Progress made
3. What's stuck
4. One insight"""
        
        return self._call_api(prompt)


class LMStudioProvider(LLMProvider):
    """LM Studio provider (OpenAI-compatible local API)."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", model: str = "local-model"):
        self.base_url = base_url.rstrip("/")
        self.model = model
    
    def _call_api(self, prompt: str, max_tokens: int = 1024) -> str:
        """Make API call to LM Studio."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"LM Studio API error: {e}")
    
    def classify(self, thought: str) -> Dict[str, Any]:
        """Classify a thought using LM Studio."""
        prompt = f"""You are a classifier for a personal knowledge system.

INPUT: {thought}

OUTPUT: Return ONLY valid JSON:
{{
  "destination": "people" | "projects" | "ideas" | "admin",
  "confidence": 0.0-1.0,
  "filename": "suggested-filename-kebab-case",
  "extracted": {{}},
  "linked_entities": []
}}"""
        
        response_text = self._call_api(prompt)
        
        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end].strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "destination": "ideas",
                "confidence": 0.5,
                "filename": thought[:30].lower().replace(" ", "-"),
                "extracted": {},
                "linked_entities": []
            }
    
    def generate_digest(self, context: Dict[str, Any]) -> str:
        """Generate daily digest."""
        prompt = f"""Generate a daily digest under 150 words.

Active projects: {len(context.get('projects', []))}
People with follow-ups: {len(context.get('people', []))}

Structure:
1. Top 3 actions for today
2. One thing you might be avoiding
3. People follow-ups"""
        
        return self._call_api(prompt, max_tokens=500)
    
    def generate_review(self, context: Dict[str, Any]) -> str:
        """Generate weekly review."""
        prompt = f"""Generate a weekly review under 250 words.

Items captured: {json.dumps(context.get('stats', {}))}
Active projects: {len(context.get('projects', []))}

Structure:
1. What you captured
2. Progress made
3. What's stuck
4. One insight"""
        
        return self._call_api(prompt, max_tokens=600)


def get_provider(provider_type: str, **kwargs) -> LLMProvider:
    """
    Factory function to get an LLM provider.
    
    Args:
        provider_type: "anthropic", "openai", "ollama", or "lmstudio"
        **kwargs: Provider-specific arguments
    
    Returns:
        LLMProvider instance
    """
    provider_type = provider_type.lower()
    
    if provider_type == "anthropic":
        api_key = kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required")
        return AnthropicProvider(api_key=api_key, model=kwargs.get("model", "claude-3-5-sonnet-20241022"))
    
    elif provider_type == "openai":
        api_key = kwargs.get("api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        return OpenAIProvider(api_key=api_key, model=kwargs.get("model", "gpt-4"))
    
    elif provider_type == "ollama":
        base_url = kwargs.get("base_url", "http://localhost:11434")
        model = kwargs.get("model", "llama2")
        return OllamaProvider(base_url=base_url, model=model)
    
    elif provider_type == "lmstudio":
        base_url = kwargs.get("base_url", "http://localhost:1234/v1")
        model = kwargs.get("model", "local-model")
        return LMStudioProvider(base_url=base_url, model=model)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def get_available_ollama_models(base_url: str = "http://localhost:11434") -> list:
    """Get list of available Ollama models."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception:
        return []


if __name__ == "__main__":
    # Test provider
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python llm_provider.py <provider_type> [args...]")
        sys.exit(1)
    
    provider_type = sys.argv[1]
    
    try:
        if provider_type == "ollama":
            models = get_available_ollama_models()
            print(f"Available Ollama models: {models}")
        else:
            provider = get_provider(provider_type)
            print(f"Provider {provider_type} initialized successfully")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
