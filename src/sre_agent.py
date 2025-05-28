
import os
import json
from typing import Any, Dict

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    SseServerParams,
    StdioServerParameters,
)
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL_PROVIDER = "openai"
REASONING_MODEL = os.getenv("ARK_REASONING_MODEL")
API_BASE = os.getenv("ARK_API_BASE")
API_KEY = os.getenv("ARK_API_KEY")


def create_reasoning_model():
    return LiteLlm(
        model=f"{MODEL_PROVIDER}/{REASONING_MODEL}",
        api_key=API_KEY,
        api_base=API_BASE,
    )


def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
):
    """Inspects/modifies tool args or skips the tool call."""
    if tool.name == "run_command":
        command = args.get("command_content", "")
        if "ls" in command:
            print("[Callback] Detected 'ls' in command. Skipping tool execution.")
            return {"result": "Tool execution was blocked by before_tool_callback."}
    return None


async def aget_sre_agent() -> tuple[LlmAgent, MCPToolset]:
    ECS_SERVICE_URL = os.getenv("ECS_SERVICE_URL")
    assert ECS_SERVICE_URL is not None

    tools = MCPToolset(
        connection_params=SseServerParams(
            url=ECS_SERVICE_URL,
        )
    )

    agent = LlmAgent(
        name="sre_agent",
        model=create_reasoning_model(),
        description="You can use mcp tools to run commands on remote ECS.",
        instruction="You can use mcp tools to run commands on remote ECS.",
        tools=[tools],
        before_tool_callback=simple_before_tool_modifier,
    )

    return agent, tools

