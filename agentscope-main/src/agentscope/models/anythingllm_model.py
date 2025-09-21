# -*- coding: utf-8 -*-
"""Model wrapper for AnythingLLM API."""
import os
import requests
from abc import ABC
from typing import Union, Any, List, Sequence, Optional

from loguru import logger
from dotenv import load_dotenv

from .model import ModelWrapperBase, ModelResponse
from ..message import Msg

# Load environment variables
load_dotenv()

class AnythingLLMWrapperBase(ModelWrapperBase, ABC):
    """The base class for AnythingLLM model wrapper."""

    def __init__(
        self,
        config_name: str,
        api_url: str = None,
        workspace_slug: str = None,
        api_key: str = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the AnythingLLM wrapper.

        Args:
            config_name (`str`):
                The name of the model config.
            api_url (`str`, default `None`):
                The API URL for AnythingLLM instance.
            workspace_slug (`str`, default `None`):
                The workspace slug to use.
            api_key (`str`, default `None`):
                The API key for AnythingLLM.
        """
        super().__init__(config_name=config_name, model_name="anythingllm")

        self.api_url = api_url or os.getenv('ANYTHINGLLM_API_URL', 'http://localhost:3001/api')
        self.workspace_slug = workspace_slug or os.getenv('ANYTHINGLLM_WORKSPACE_SLUG', 'scientific-papers')
        self.api_key = api_key or os.getenv('ANYTHINGLLM_API_KEY')
        
        if not self.api_key:
            raise ValueError("AnythingLLM API key is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def format(
        self,
        *args: Union[Msg, Sequence[Msg]],
    ) -> str:
        """Format the input messages into a single string for AnythingLLM."""
        input_msgs = []
        for _ in args:
            if _ is None:
                continue
            if isinstance(_, Msg):
                input_msgs.append(_)
            elif isinstance(_, list) and all(isinstance(__, Msg) for __ in _):
                input_msgs.extend(_)
            else:
                raise TypeError(
                    f"The input should be a Msg object or a list "
                    f"of Msg objects, got {type(_)}.",
                )

        # Combine all messages into a single prompt
        prompt_parts = []
        for msg in input_msgs:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            else:
                prompt_parts.append(f"{msg.name}: {msg.content}")
        
        return "\n".join(prompt_parts)


class AnythingLLMChatWrapper(AnythingLLMWrapperBase):
    """The model wrapper for AnythingLLM chat API."""

    model_type: str = "anythingllm_chat"

    def __init__(
        self,
        config_name: str,
        api_url: str = None,
        workspace_slug: str = None,
        api_key: str = None,
        temperature: float = 0.5,
        mode: str = "chat",
        **kwargs: Any,
    ) -> None:
        """Initialize the AnythingLLM chat wrapper.

        Args:
            config_name (`str`):
                The name of the model config.
            api_url (`str`, default `None`):
                The API URL for AnythingLLM instance.
            workspace_slug (`str`, default `None`):
                The workspace slug to use.
            api_key (`str`, default `None`):
                The API key for AnythingLLM.
            temperature (`float`, default `0.5`):
                The temperature for generation.
            mode (`str`, default `"chat"`):
                The chat mode - "chat" for RAG-enabled, "query" for simple query.
        """
        super().__init__(
            config_name=config_name,
            api_url=api_url,
            workspace_slug=workspace_slug,
            api_key=api_key,
            **kwargs,
        )
        
        self.temperature = temperature
        self.mode = mode

    def __call__(
        self,
        messages: Union[str, List[dict]],
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> ModelResponse:
        """Send a chat request to AnythingLLM.

        Args:
            messages (`Union[str, List[dict]]`):
                The formatted messages or prompt string.
            mode (`Optional[str]`, default `None`):
                Override the default chat mode.
            **kwargs (`Any`):
                Additional arguments.

        Returns:
            `ModelResponse`:
                The response from AnythingLLM.
        """
        # Convert messages to string if needed
        if isinstance(messages, list):
            prompt = self.format(*messages)
        else:
            prompt = messages

        url = f"{self.api_url}/v1/workspace/{self.workspace_slug}/chat"
        
        payload = {
            "message": prompt,
            "mode": mode or self.mode
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            text_response = response_data.get("textResponse", "")
            
            # Record the API invocation
            self._save_model_invocation(
                arguments=payload,
                response=response_data,
            )

            return ModelResponse(
                text=text_response,
                raw=response_data,
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling AnythingLLM API: {e}")
            raise RuntimeError(f"Failed to call AnythingLLM API: {e}")