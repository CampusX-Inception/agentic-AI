import random
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool


@tool
def take_sensor_reading() -> float:
    """Take a sensor reading. Returns a float between 0 and 10."""
    reading = round(random.uniform(0, 10), 2)
    print(f"Sensor reading: {reading}")
    return reading

@tool
def turn_on_pump() -> str:
    """Turn on the pump."""
    print("\n")
    print("Action: Turning on pump")
    return "Pump is on"

@tool
def turn_on_ac() -> str:
    """Turn on the AC."""
    print("\n")
    print("Action: Turning on AC")
    return "AC is on"


model = ChatOpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
    model="qwen/qwen3-235b-a22b",
    temperature=0.2,
)

tools = [take_sensor_reading, turn_on_pump, turn_on_ac]

agent = create_agent(
    model.bind_tools(tools, parallel_tool_calls=False),
    tools,
    system_prompt="""You are an environment controller. Follow these rules strictly:
1. Always call take_sensor_reading first.
2. If reading > 5: call turn_on_pump, then call turn_on_ac.
3. If reading > 2 but <= 5: call turn_on_pump only.
4. If reading <= 2: do nothing.
5. when in doubt, do the first thing that comes to mind, don't overthink it.
"""
)

agent.invoke({"messages": [{"role": "user", "content": "Check the sensor and act."}]})



