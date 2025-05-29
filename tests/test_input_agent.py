from dotenv import load_dotenv
load_dotenv()
from google.adk.agents import LlmAgent
from google.adk.tools.load_memory_tool import load_memory,LoadMemoryTool,load_memory_tool

from src.utils.times import get_current_time


import os
import asyncio
import inspect
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)
from src.memory.vdb_memory import VdbMemory
from src.retrieval.vdb import VectorType
from src.sre_agent import aget_sre_agent, create_reasoning_model
from src.tools.kb_tools import prepare_data
from src.utils.misc import filter
filter()


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
        tools=[tools, load_memory_tool],
    )

    return agent, tools

APP_NAME = "ecs_app"            # 由于memory用到opensearch或者chroma，而他们对index-name有要求
USER_ID = "user_02"             # 故app-name和user-id目前仅限使用数字+小写字母+连字符+下划线，且首尾为小写字母或数字
SESSION_ID = "session_02"


async def run():
    agent, tools = await aget_time_agent()
    # set session
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    # set memory
    memory_service = VdbMemory(vector_type=VectorType.CHROMA.value)     # 测试的时候采用chromadb，不会持久化方便我测试

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service
    )
    # for循环中的一次迭代，为一轮对话；完整for循环为一整个会话
    while True:
        prompt = input("请输入内容（输入exit退出）: ").strip()
        if prompt.lower() == "exit":  # 不区分大小写
            print("程序已退出")
            break

        message = types.Content(
            role="user", parts=[
                types.Part(text=prompt)
            ]
        )
        async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=message
        ):
            if event.content.parts[0].text is not None and len(event.content.parts[0].text.strip())>0:
                print(f"Model:{event.content.parts[0].text.strip()}")

            print()
        print("-"*130)

    await tools.close()


if __name__ == "__main__":
    # export PYTHONPATH=.
    # python examples/main.py
    # # 事先存储知识库
    # prepare()


    asyncio.run(run())
