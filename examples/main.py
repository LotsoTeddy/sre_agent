from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import inspect
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from utils.logger import get_logger
from src.sre_agent import aget_sre_agent
from src.utils.misc import filter
filter()
logger = get_logger(__name__)

APP_NAME = "ecs_app"
USER_ID = "user_id"
SESSION_ID = "session_id"

# 先不用管记忆的事儿

async def run(prompts: list[str]):
    agent, tools = await aget_sre_agent()
    # set session
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    for prompt in prompts:
        message = types.Content(
            role="user", parts=[
                types.Part(text=prompt)
            ]
        )
        async for event in runner.run_async(
                user_id=USER_ID, session_id=SESSION_ID, new_message=message
        ):
            if event.content.parts[0].text is not None and len(event.content.parts[0].text.strip())>0:
                logger.info(f"\nPrompt: {prompt}")
                logger.info(f"\nEvent received: \ntext:{event.content.parts[0].text.strip()}")
            else:
                print(f"\nEvent received: \nevent:{dict(event.content.parts[0])}")
            print()
        print("-"*130)
        await tools.close()

    logger.info("Ending --------------------------------")

if __name__ == "__main__":
    prompts = [

    ]
    asyncio.run(run(prompts))