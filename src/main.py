from dotenv import load_dotenv
from agents.gemini_agent import build_gemini_agent
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    load_dotenv()
    print("✅ Environment variables loaded successfully.")

    agent = build_gemini_agent()

    while True:
        q = input("\n🧑 User: ")
        if q.lower() in ["exit", "quit"]:
            break
        response = agent.run(q)
        print(f"\n🤖 Agent: {response}")

if __name__ == "__main__":
    main()
