# -*- coding: utf-8 -*-
"""
The customized scientist agent in this project
"""

from typing import Any, Optional, Union, Sequence
from loguru import logger

from agentscope.agents.agent import AgentBase
from agentscope.message import Msg


class SciAgent(AgentBase):
    """
    A scientist agent that uses AnythingLLM for knowledge retrieval and generation.
    """

    def __init__(
            self,
            name: str,
            sys_prompt: str,
            model_config_name: str,
            anythingllm_client = None,
            **kwargs: Any,
    ) -> None:
        """
        Initialize the SciAgent
        Args:
            name (str):
                the name for the agent
            sys_prompt (str):
                system prompt for the RAG agent
            model_config_name (str):
                language model for the agent
            anythingllm_client:
                AnythingLLM client for API interactions
        """
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model_config_name=model_config_name,
        )
        self.anythingllm_client = anythingllm_client
        self.description = kwargs.get("description", "")

    def format_msg(self, *input: Union[Msg, Sequence[Msg]]) -> list:
        """Forward the input to the model.

        Args:
            input (`Union[Msg, Sequence[Msg]]`):
                The input arguments to be formatted, where each argument
                should be a `Msg` object, or a list of `Msg` objects.
                In distribution, placeholder is also allowed.

        Returns:
            `list`:
                The formatted message list.
        """
        input_msgs = []
        for _ in input:
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

        return input_msgs

    def prompt_reply(self, x: Optional[Union[Msg, Sequence[Msg]]] = None, use_RAG = True, add_memory: bool = True, use_memory = True) -> Msg:
        """Generate a reply using AnythingLLM."""
        if x is not None:
            x = self.format_msg(x)
            query = (
                "\n".join(
                    [msg["content"] for msg in x],
                )
            )
        else:
            query = ""
        
        # prepare prompt
        prompt_parts = [f"System: {self.sys_prompt}"]
        
        if use_memory:
            memory = self.memory.get_memory(recent_n=2)
            for mem in memory:
                prompt_parts.append(f"{mem.name}: {mem.content}")
        
        if query:
            prompt_parts.append(f"User: {query}")
        
        prompt = "\n".join(prompt_parts)

        # Determine chat mode based on use_RAG
        chat_mode = "chat" if use_RAG else "query"
        
        # Call AnythingLLM API
        if self.anythingllm_client:
            response_data = self.anythingllm_client.chat_with_workspace(prompt, mode=chat_mode)
            response_text = response_data.get("textResponse", "")
        else:
            # Fallback to direct model call
            response = self.model(prompt)
            response_text = response.text

        msg = Msg(self.name, response_text)

        # Print/speak the message in this agent's voice
        self.speak(msg)

        if self.memory and add_memory:
            # Record the message in memory
            self.memory.add(msg)

        return msg
        
    
    def summarize(self, history: Optional[Union[Msg, Sequence[Msg]]] = None,
                  content: Optional[Union[Msg, Sequence[Msg]]] = None) -> str:
        """Summarize content using AnythingLLM."""
        prompt_parts = []
        
        if history is not None:
            history_msgs = self.format_msg(history)
            for msg in history_msgs:
                prompt_parts.append(f"{msg.name}: {msg.content}")
            prompt_parts.append("System: Based on the context above, summarize the following content in a concise manner, capturing the key points of the content and any important decisions or actions discussed. Do not summarize repeated content which is already existed in the context above!")
        else:
            prompt_parts.append("System: Summarize the following content in a concise manner, capturing the key points of the content and any important decisions or actions discussed.")
        
        if content is not None:
            content_msgs = self.format_msg(content)
            for msg in content_msgs:
                prompt_parts.append(f"{msg.name}: {msg.content}")
        
        prompt = "\n".join(prompt_parts)

        # Call AnythingLLM API for summarization (use query mode for focused response)
        if self.anythingllm_client:
            response_data = self.anythingllm_client.chat_with_workspace(prompt, mode="query")
            response_text = response_data.get("textResponse", "")
        else:
            response = self.model(prompt)
            response_text = response.text

        msg = Msg(self.name, response_text)

        # Print/speak the message in this agent's voice
        self.speak(msg)

        return msg

    def reply(self, x: Optional[Union[Msg, Sequence[Msg]]] = None, use_RAG=True, use_memory=True) -> Msg:
        """
        Reply function using AnythingLLM.

        Args:
            x (`Optional[Union[Msg, Sequence[Msg]]]`, defaults to `None`):
                The input message(s) to the agent, which also can be omitted if
                the agent doesn't need any input.
            use_RAG (`bool`, defaults to `True`):
                Whether to use RAG capabilities through AnythingLLM.
            use_memory (`bool`, defaults to `True`):
                Whether to use conversation memory.

        Returns:
            `Msg`: The output message generated by the agent.
        """
        if self.memory:
            self.memory.add(x)
            
        elif x is not None:
            if isinstance(x, list):
                query = "\n".join([msg.content for msg in x])
            else:
                query = x.content
        else:
            query = ""
        
        # Prepare prompt
        prompt_parts = [f"System: {self.sys_prompt}"]
        
        if use_memory and self.memory:
            memory = self.memory.get_memory(recent_n=2)
            for mem in memory:
                prompt_parts.append(f"{mem.name}: {mem.content}")
        
        prompt = "\n".join(prompt_parts)
                ),
            )
        else:
            prompt = self.model.format(
                Msg(
                    name="system",
                    role="system",
                    content=self.sys_prompt,
                ),
                Msg(
                    name="user",
                    role="user",
                    content="Context: " + retrieved_docs_to_string,
                ),
                x
            )

        # Determine chat mode
        chat_mode = "chat" if use_RAG else "query"
        
        # Call AnythingLLM API
        if self.anythingllm_client:
            response_data = self.anythingllm_client.chat_with_workspace(prompt, mode=chat_mode)
            response_text = response_data.get("textResponse", "")
        else:
            response = self.model(prompt)
            response_text = response.text

        msg = Msg(self.name, response_text)

        # Print/speak the message in this agent's voice
        self.speak(msg)

        if self.memory:
            # Record the message in memory
            self.memory.add(msg)

        return msg
