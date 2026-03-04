"""Ollama LLM client for local model inference"""
import logging
from dataclasses import dataclass
from typing import List
import aiohttp

from .llm_client import ChatMessage

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration for Ollama client"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2:latest"
    temperature: float = 0.7
    timeout: float = 30.0


class OllamaClient:
    """Ollama LLM client

    Connects to local Ollama server for LLM inference.
    Compatible with MockLLMClient interface for easy switching.
    """

    def __init__(self, config: OllamaConfig = None):
        """Initialize Ollama client

        Args:
            config: OllamaConfig instance. If None, uses defaults.
        """
        self.config = config or OllamaConfig()
        self.api_url = f"{self.config.base_url}/api/chat"

    async def chat(self, messages: List[ChatMessage]) -> str:
        """Send chat request to Ollama

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Assistant's response text

        Raises:
            ValueError: If messages are invalid
            ConnectionError: If cannot connect to Ollama
            Exception: If Ollama API returns error
        """
        # Validate messages
        self._validate_messages(messages)

        # Build request payload
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,  # Use non-streaming mode for simplicity
            "options": {
                "temperature": self.config.temperature
            }
        }

        # Call Ollama API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(
                            f"Ollama API error (status {response.status}): {error_text}"
                        )

                    result = await response.json()
                    return result["message"]["content"]

        except ConnectionError as e:
            logger.error(f"Failed to connect to Ollama at {self.config.base_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def _validate_messages(self, messages: List[ChatMessage]) -> None:
        """Validate message list

        Args:
            messages: List of messages to validate

        Raises:
            ValueError: If validation fails
        """
        # Check not empty
        if not messages:
            raise ValueError("Messages list cannot be empty")

        # Validate each message
        for msg in messages:
            # Check required fields
            if "role" not in msg or "content" not in msg:
                raise ValueError(
                    "Invalid message format: missing 'role' or 'content' field"
                )

            # Check types
            if not isinstance(msg["role"], str):
                raise ValueError("Invalid message format: 'role' must be a string")

            if not isinstance(msg["content"], str):
                raise ValueError("Invalid message format: 'content' must be a string")

            # Check content not empty
            if not msg["content"].strip():
                raise ValueError("Message content cannot be empty")

        # Check at least one user message
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            raise ValueError("Messages must contain at least one user message")
