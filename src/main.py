from src.agents.workflow import workflow

if __name__ == "__main__":
    state = {"user_input": "My name is Rahul Mehta, DOB 1990-05-15", "messages": []}
    result = workflow.invoke(state)
    for msg in result["messages"]:
        print("Agent:", msg)
