import asyncio
import inspect
import json

from arkitect.core.component.context.context import Context
from arkitect.core.component.tool.mcp_client import MCPClient
from examples.prompts import CEA_SYSTEM_PROMPT, IUA_SYSTEM_PROMPT, RAA_SYSTEM_PROMPT
from src.knowledgebase import KnowledgeBase
from src.memory import LongTermMemory, ShortTermMemory
from src.SREAgent import SREAgent
from src.utils.misc import filter_log

filter_log()

DEFAULT_LLM = "doubao-1-5-pro-256k-250115"

APP_NAME = "Intelligent SRE"
USER_ID = "SREer"

MCP_INFO = ""
mcp_client = MCPClient(
    name="ecs_mcp_client",
    server_url=MCP_INFO,
)


agent_configs = [
    {
        "name": "Intention Understanding Agent",
        "description": "An agent that understand the user's intention",
        "instruction": IUA_SYSTEM_PROMPT,
        "knowledgebase": None,
        "short_term_memory": ShortTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=0
        ),
        "long_term_memory": LongTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=0
        ),
    },
    {
        "name": "Risk Analyzer Agent",
        "description": "An agent that analyze the risk of the command",
        "instruction": RAA_SYSTEM_PROMPT,
        "knowledgebase": None,
        "short_term_memory": ShortTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=1
        ),
        "long_term_memory": LongTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=1
        ),
    },
    {
        "name": "Command Executor Agent",
        "description": "An agent that execute the command",
        "instruction": CEA_SYSTEM_PROMPT,
        "knowledgebase": None,
        "short_term_memory": ShortTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=2
        ),
        "long_term_memory": LongTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=2
        ),
    },
]


async def main(prompt: str):
    # model = Context(model=DEFAULT_LLM, tools=[])
    # await model.init()

    model_mcp = Context(model=DEFAULT_LLM, tools=[mcp_client])
    await model_mcp.init()

    agent = SREAgent(**agent_configs[2], model=model_mcp)

    response = await agent.run(prompt)
    print(response)

    await mcp_client.cleanup()


if __name__ == "__main__":
    prompt = ""
    asyncio.run(main(prompt))
