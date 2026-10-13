"""Reusable LLM provider abstractions with sanitized error handling."""

from abc import ABC, abstractmethod
from socket import timeout
from dotenv import load_dotenv
import io
import json
import os
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request
import ssl
import certifi
load_dotenv()


class LLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> str:
        """Generate a text completion for the given prompt."""
        pass


class FakeLLMProvider(LLMProvider):
    """Deterministic fake LLM provider for hermetic testing and fallback.

    Allows tests to simulate successful completions, input extraction,
    unrecognized requests, invalid IDs, malformed JSON, and timeouts/errors
    without calling an external API.
    """

    def __init__(
        self,
        responses: Optional[Dict[str, str]] = None,
        default_response: Optional[str] = None,
        error_to_raise: Optional[Exception] = None,
    ) -> None:
        self.responses: Dict[str, str] = responses or {}
        self.default_response: Optional[str] = default_response
        self.error_to_raise: Optional[Exception] = error_to_raise
        self.call_history: List[Dict[str, Any]] = []

    def set_response(self, query_keyword: str, response_json: str) -> None:
        """Register a canned response triggered by a keyword in the prompt."""
        self.responses[query_keyword.lower()] = response_json

    def set_error(self, error: Optional[Exception]) -> None:
        """Configure the fake provider to raise an exception."""
        self.error_to_raise = error

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> str:
        self.call_history.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "timeout": timeout,
        })

        if self.error_to_raise:
            raise self.error_to_raise

        prompt_lower = prompt.lower()
        for keyword, resp in self.responses.items():
            if keyword in prompt_lower:
                return resp

        if self.default_response is not None:
            return self.default_response

        # Fallback clarification response if no canned match
        return json.dumps({
            "workflow_id": None,
            "confidence": 0.0,
            "reasoning": "FakeLLMProvider found no canned match for the request.",
            "extracted_inputs": {},
            "requires_clarification": True,
        })


class OpenAICompatibleProvider(LLMProvider):
    """Lightweight HTTP provider for OpenAI or OpenAI-compatible endpoints.

    Uses standard library urllib to avoid heavy third-party SDK dependencies.
    Reads credentials from environment variables; never logs or prints secrets.
    Sanitizes all exceptions to avoid leaking HTTP error response bodies or headers.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = (
            base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ).rstrip("/")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> str:
        if not self._api_key:
            raise ValueError(
                "OpenAI API key is missing. Please set OPENAI_API_KEY in the environment."
            )

        endpoint = f"{self.base_url}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            # Drain response body to close connection cleanly without exposing content
            try:
                exc.read()
            except Exception:
                pass
            status_text = f"HTTP {exc.code}"
            if exc.reason:
                status_text += f" ({exc.reason})"
            raise RuntimeError(
                f"OpenAI API request failed: {status_text}."
            ) from None
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", "connection failed")
            raise ConnectionError(
                f"Failed to connect to OpenAI API endpoint: {reason}."
            ) from None


class GeminiProvider(LLMProvider):
    """Lightweight HTTP provider for Google Gemini REST API.

    Uses standard library urllib without requiring external Google SDKs.
    Passes credentials via the x-goog-api-key HTTP header rather than query params
    to prevent credentials from appearing in request URLs or stack traces.
    Sanitizes all exceptions to avoid leaking HTTP error response bodies or secrets.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> str:
        if not self._api_key:
            raise ValueError(
                "Gemini API key is missing. Please set GEMINI_API_KEY in the environment."
            )

        # Do not include key in query params to avoid credential exposure in URLs/traces
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instructions: {system_prompt}"}],
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will strictly follow these instructions and return JSON."}],
            })
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}],
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json",
            },
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                req,
                timeout=timeout,
                context=ssl.create_default_context(cafile=certifi.where()),
            ) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as exc:
            # Drain response body to close connection cleanly without exposing content
            try:
                exc.read()
            except Exception:
                pass
            status_text = f"HTTP {exc.code}"
            if exc.reason:
                status_text += f" ({exc.reason})"
            raise RuntimeError(
                f"Gemini API request failed: {status_text}."
            ) from None
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", "connection failed")
            raise ConnectionError(
                f"Failed to connect to Gemini API endpoint: {reason}."
            ) from None


def get_llm_provider(
    provider_name: Optional[str] = None,
    **kwargs: Any,
) -> LLMProvider:
    """Factory function to instantiate an LLM provider based on environment or explicit name.

    When no live provider (OpenAI or Gemini) is configured, returns a safe FakeLLMProvider
    that explicitly notifies the caller that live LLM routing is inactive.
    """
    name = (provider_name or os.getenv("LLM_PROVIDER", "")).strip().lower()

    if name == "fake":
        return FakeLLMProvider(**kwargs)
    elif name == "gemini":
        return GeminiProvider(**kwargs)
    elif name == "openai":
        return OpenAICompatibleProvider(**kwargs)

    # Auto-detect from present API keys
    if os.getenv("GEMINI_API_KEY"):
        return GeminiProvider(**kwargs)
    if os.getenv("OPENAI_API_KEY"):
        return OpenAICompatibleProvider(**kwargs)

    # Explicit fallback: live LLM routing is inactive
    return FakeLLMProvider(
        default_response=json.dumps({
            "workflow_id": None,
            "confidence": 0.0,
            "reasoning": (
                "Live LLM provider is not configured (no active OPENAI_API_KEY or "
                "GEMINI_API_KEY detected). Automated routing is inactive; clarification required."
            ),
            "extracted_inputs": {},
            "requires_clarification": True,
        }),
        **kwargs,
    )


def is_live_llm_configured() -> bool:
    """Return True if live LLM credentials (Gemini or OpenAI) are active in the environment."""
    provider_name = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider_name in ("gemini", "openai"):
        return True
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
