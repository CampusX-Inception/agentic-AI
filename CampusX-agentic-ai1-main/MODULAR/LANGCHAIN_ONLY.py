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
    print("Action: Turning on pump")
    return "Pump is on"

@tool
def turn_on_ac() -> str:
    """Turn on the AC."""
    print("Action: Turning on AC")
    return "AC is on"


model = ChatOpenAI(
    api_key="add-api-key-here",
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3-0324",
    temperature=0.2,
)

tools = [take_sensor_reading, turn_on_pump, turn_on_ac]

agent = create_agent(
    model.bind_tools(tools, parallel_tool_calls=False),
    tools,
    system_prompt="""You are an environment controller. Follow these rules strictly:
1. Always call take_sensor_reading first.
2. If reading > 8: call turn_on_pump, then call turn_on_ac.
3. If reading > 5 but <= 8: call turn_on_pump only.
4. If reading <= 5: do nothing."""
)

agent.invoke({"messages": [{"role": "user", "content": "Check the sensor and act."}]})

