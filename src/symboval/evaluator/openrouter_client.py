"""OpenRouter API client for LLM evaluation."""
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import urllib.request
import urllib.error


@dataclass
class ModelResponse:
    """Response from an LLM model."""
    model: str
    response: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float
    raw_response: Dict[str, Any]


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, site_url: Optional[str] = None, app_name: Optional[str] = None):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            site_url: Optional URL of your site (for rankings on openrouter.ai)
            app_name: Optional name of your app (for rankings on openrouter.ai)
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required")

        self.api_key = api_key
        self.site_url = site_url or "https://github.com/ysarda/symboval"
        self.app_name = app_name or "Symboval"

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter.

        Returns:
            List of model information dictionaries
        """
        url = f"{self.BASE_URL}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data.get("data", [])
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"Failed to fetch models: {e.code} - {error_body}")

    def complete(
        self,
        prompt: str,
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 1.0,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """Send a completion request to OpenRouter.

        Args:
            prompt: The prompt to send to the model
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            system_prompt: Optional system prompt
            **kwargs: Additional parameters to pass to the API

        Returns:
            ModelResponse object with the completion
        """
        url = f"{self.BASE_URL}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            **kwargs
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }

        start_time = time.time()

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                latency = time.time() - start_time

                choice = data["choices"][0]
                usage = data.get("usage", {})

                return ModelResponse(
                    model=data.get("model", model),
                    response=choice["message"]["content"],
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    latency=latency,
                    raw_response=data
                )

        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"OpenRouter API error: {e.code} - {error_body}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse OpenRouter response: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected response format from OpenRouter: {e}")

    def batch_complete(
        self,
        prompts: List[str],
        model: str = "anthropic/claude-3.5-sonnet",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
        delay: float = 0.5,
        **kwargs
    ) -> List[ModelResponse]:
        """Send multiple completion requests with rate limiting.

        Args:
            prompts: List of prompts to send
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
            system_prompt: Optional system prompt
            delay: Delay between requests in seconds
            **kwargs: Additional parameters

        Returns:
            List of ModelResponse objects
        """
        responses = []
        for i, prompt in enumerate(prompts):
            try:
                response = self.complete(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    **kwargs
                )
                responses.append(response)

                # Add delay between requests to avoid rate limiting
                if i < len(prompts) - 1:
                    time.sleep(delay)

            except Exception as e:
                print(f"Error processing prompt {i+1}/{len(prompts)}: {e}")
                # Create a failed response
                responses.append(ModelResponse(
                    model=model,
                    response="",
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency=0.0,
                    raw_response={"error": str(e)}
                ))

        return responses