from src.SREAgent import SREAgent

from .prompts import CEA_SYSTEM_PROMPT, IUA_SYSTEM_PROMPT, RAA_SYSTEM_PROMPT

DEFAULT_LLM = ""


def build_agents():
    intention_understanding_agent = SREAgent(
        system_prompt=IUA_SYSTEM_PROMPT,
        model=DEFAULT_LLM,
        tools=[],
    )
    risk_analyzer_agent = SREAgent(
        system_prompt=RAA_SYSTEM_PROMPT,
        model=DEFAULT_LLM,
        tools=[],
    )
    command_executor_agent = SREAgent(
        system_prompt=CEA_SYSTEM_PROMPT,
        model=DEFAULT_LLM,
        tools=[],
    )
    return [intention_understanding_agent, risk_analyzer_agent, command_executor_agent]


def main(prompt: str):
    agents = build_agents()
    for agent in agents:
        prompt = agent.run(prompt)
        print(prompt)


if __name__ == "__main__":
    main()
