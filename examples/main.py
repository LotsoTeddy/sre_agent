import json

from examples.prompts import CEA_SYSTEM_PROMPT, IUA_SYSTEM_PROMPT, RAA_SYSTEM_PROMPT
from src.knowledgebase import KnowledgeBase
from src.memory import LongTermMemory, ShortTermMemory
from src.SREAgent import SREAgent

DEFAULT_LLM = "doubao-1.5-pro-32k-250115"

APP_NAME = "Intelligent SRE"
USER_ID = "SREer"

agent_configs = [
    {
        "name": "Intention Understanding Agent",
        "description": "An agent that understand the user's intention",
        "instruction": IUA_SYSTEM_PROMPT,
        "model": DEFAULT_LLM,
        "tools": [],
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
        "model": DEFAULT_LLM,
        "tools": [],
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
        "model": DEFAULT_LLM,
        "tools": [],
        "knowledgebase": None,
        "short_term_memory": ShortTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=2
        ),
        "long_term_memory": LongTermMemory(
            app_name=APP_NAME, user_id=USER_ID, session_id=2
        ),
    },
]


def main(prompt: str):
    agents = [
        SREAgent(**agent_configs[0]),
        SREAgent(**agent_configs[1]),
        SREAgent(**agent_configs[2]),
    ]

    print(f"The initial prompt is: {prompt}")

    command = agents[0].run(prompt)
    print(f"The command is: {command}")

    risk_detection = agents[1].run(command)
    risk_detection = json.loads(risk_detection)
    if risk_detection["is_high_risk"]:
        print(f"The command is high risk: {risk_detection['reason']}")
        return

    print(f"The command is low risk, continue to execute.")
    command_result = agents[2].run(command)
    print(f"The command result is: {command_result}")


if __name__ == "__main__":
    main("Tell me the CPU usage")
