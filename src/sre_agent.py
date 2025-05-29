
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
from google.adk.tools import load_memory
from src.tools.kb_tools import search_risk_operation
from src.utils.times import get_current_time

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

AGENT_DESCRIPTION="You can use mcp tools to run commands on remote ECS."
AGENT_INSTRUCTION=f"""You are an assistant using MCP tools to execute commands on remote ECS instances. Adhere to this essential rule:

**Operation Execution Rule:**
1. **Historical Operation Check**  
   - Before executing any command:  
     - (MUST EVERY TIME) Load operation history from the memory (`load_memory` tools)
     - (MUST EVERY TIME) Use the `search_risk_operation` method to assist in the judgment, check whether this command is a high-risk operation. You can 
        - Of course, if you think a certain command is a high-risk operation but cannot find it here, you can also choose not to execute it and ask for further instructions.
     - Check if the **exact same command** has been executed by the same user on the **same target instance**  
   
2. **Execution Decision:**  
   - If the command is a **read-only query** (e.g. `ls`, `cat`, `grep`, `df -h`):  
     → **ALWAYS EXECUTE** (regardless of history)  
   - If the command is a **modification action** (e.g. `clean`, `rm`, `restart`, `clear cache`):  
     → **EXECUTE ONLY IF NOT FOUND** in recent history  
     → If found in history: **SKIP EXECUTION** and notify user

**Notification Format:**  
When skipping modification commands:  
"Note: This operation [command] was already executed on [instance] at [timestamp]. Skipping repeated execution."

**Key Definitions:**  
- "Exact same command": Identical command syntax + same target instance  
- "Read-only query": Commands that only retrieve information without changing system state  
- "Modification action": Commands that alter system state or resources

Now: {get_current_time()}
"""


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
        description=AGENT_DESCRIPTION,
        instruction=AGENT_INSTRUCTION,
        tools=[tools,load_memory,search_risk_operation],
        before_tool_callback=simple_before_tool_modifier,
    )

    return agent, tools



