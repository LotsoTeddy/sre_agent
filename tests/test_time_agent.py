"""
此脚本用于验证 Agent的长期记忆能力
"""

from dotenv import load_dotenv
load_dotenv()
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import load_memory
from src.utils.times import get_current_time
from src.memory.vdb_memory import VdbMemory
from src.retrieval.vdb import VectorType
from src.sre_agent import create_reasoning_model
from src.utils.misc import filter
filter()
from src.utils.logger import get_logger
logger = get_logger(__name__)

APP_NAME = "ecs_app"            # 由于memory用到opensearch或者chroma，而他们对index-name有要求
USER_ID = "user_01"             # 故app-name和user-id目前仅限使用数字+小写字母+连字符+下划线，且首尾为小写字母或数字
SESSION_ID = "session_01"


async def aget_time_agent() -> tuple[LlmAgent, MCPToolset]:
    tools = MCPToolset(
        connection_params=StdioServerParameters(
            command="python",
            args=[
                "-m", "mcp_server_time",
                "--local-timezone", "Asia/Shanghai"
            ]

        )
    )

    agent = LlmAgent(
        name='time_agent',
        model=create_reasoning_model(),
        description="你来管理跟时间有关的内容",
        instruction=f"你来管理跟时间有关的内容，注意，如果该用户在最近一分钟的会话中已经查找过了某个城市的时间，就不允许再次查询了，当前时间为{get_current_time()}",
        tools=[tools, load_memory],
    )

    return agent, tools


async def run(prompts: list[str]):
    agent, tools = await aget_time_agent()
    # set session
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    # set memory
    memory_service = VdbMemory(vector_type=VectorType.CHROMA.value)

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service
    )
    # 一个for循环模拟一个会话
    for prompt in prompts:
        message = types.Content(
            role="user", parts=[
                types.Part(text=prompt)
            ]
        )
        logger.info(f"\nPrompt: {prompt}")
        async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=message
        ):
            if event.content.parts[0].text is not None and len(event.content.parts[0].text.strip())>0:
                logger.info(f"\nEvent received: \ntext:{event.content.parts[0].text.strip()}")
            else:
                print(f"\nEvent received: \nevent:{dict(event.content.parts[0])}")
            print()


        print("-"*130)

    # end of for loop - (a session)
    print("\n--- Adding Session 1 to Memory ---")
    completed_session1 = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    await memory_service.add_session_to_memory(completed_session1)
    await tools.close()

    logger.info("Ending --------------------------------")

if __name__ == "__main__":
    prompts = [
        "请输出现在的北京时间",
        "假设有一个地方比我刚才说的地方早一个小时，且该城市位于北半球，那么他有可能是哪些城市？"
    ]
    asyncio.run(run(prompts))

    prompts = [
        "请输出现在的北京时间",
    ]
    asyncio.run(run(prompts))