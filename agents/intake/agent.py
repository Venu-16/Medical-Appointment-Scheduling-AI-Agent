from langchain import create_agent, tool
from pydantic import BaseModel
from typing import TypeAdapter
import operator

# Define tools with @tool decorator
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is sunny, 72°F"

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Create agent with model, tools, and optional system prompt
agent = create_agent(
    model="gpt-4o-mini",  # or "openai:gpt-4o", ChatOpenAI(...)
    tools=[get_weather, multiply],
    system_prompt="You are a helpful assistant with access to tools."
)

# Invoke with user messages
result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in SF? Also compute 12*15."}]
})
print(result["messages"][-1]["content"])