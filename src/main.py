# src/main.py
import os
from dotenv import load_dotenv
from agents.scheduler_agent import build_scheduler_graph

def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("❌ GEMINI_API_KEY not found in environment.")

    print("✅ Environment variables loaded successfully.")

    # Initialize scheduler graph
    scheduler_graph = build_scheduler_graph()
    app = scheduler_graph.compile()

    # Run a dummy test
    result = app.invoke({"user_input": "Cancel Alice’s appointment"})
    print("🤖 Agent Output:\n", result["response"])


if __name__ == "__main__":
    main()
