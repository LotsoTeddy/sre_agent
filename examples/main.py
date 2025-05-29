from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import inspect
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.memory.vdb_memory import VdbMemory
from src.retrieval.vdb import VectorType
from src.sre_agent import aget_sre_agent
from src.tools.kb_tools import prepare_data
from src.utils.misc import filter
filter()
from src.utils.logger import get_logger
logger = get_logger(__name__)

APP_NAME = "ecs_app"            # 由于memory用到opensearch或者chroma，而他们对index-name有要求
USER_ID = "user_01"             # 故app-name和user-id目前仅限使用数字+小写字母+连字符+下划线，且首尾为小写字母或数字
SESSION_ID = "session_01"

def prepare():
    prepare_data("risky_comands.txt")
    logger.info("risky commands 加载成功")

async def run(prompts: list[str]):
    agent, tools = await aget_sre_agent()
    # set session
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    # set memory
    memory_service = VdbMemory(vector_type=VectorType.CHROMA.value)     # 暂时先用这个，因为chromadb不会持久化方便我测试

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service
    )
    # for循环中的一次迭代，为一轮对话；完整for循环为一整个会话
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

    completed_session = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    await memory_service.add_session_to_memory(completed_session)
    await tools.close()

    logger.info("Ending --------------------------------")

if __name__ == "__main__":
    # export PYTHONPATH=.
    # python examples/main.py
    # 事先存储知识库
    prepare()

    # 第0次会话，体现long term memory能力
    logger.info("\n第0次操作")
    prompts = [

    ]
    asyncio.run(run(prompts))

    # 正式对话
    logger.info("\n正式操作")
    prompts = [

    ]
    asyncio.run(run(prompts))