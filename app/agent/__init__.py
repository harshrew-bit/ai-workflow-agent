"""Agent and routing interfaces."""

from app.agent.prompts import ROUTING_SYSTEM_PROMPT, build_routing_user_prompt, format_workflow_catalog
from app.agent.provider import (
    FakeLLMProvider,
    GeminiProvider,
    LLMProvider,
    OpenAICompatibleProvider,
    get_llm_provider,
)
from app.agent.router import LLMWorkflowRouter, RoutingDecision, WorkflowRouter

__all__ = [
    "RoutingDecision",
    "WorkflowRouter",
    "LLMWorkflowRouter",
    "LLMProvider",
    "FakeLLMProvider",
    "OpenAICompatibleProvider",
    "GeminiProvider",
    "get_llm_provider",
    "ROUTING_SYSTEM_PROMPT",
    "build_routing_user_prompt",
    "format_workflow_catalog",
]
