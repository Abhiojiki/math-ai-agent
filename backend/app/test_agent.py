import sys
from pathlib import Path
# sys.path.append(str(Path(__file__).parent.parent / "backend" / "app"))

from agent import get_agent
from config import settings
print(f"Config SCORE_THRESHOLD: {settings.SCORE_THRESHOLD}")

def run():
    agent = get_agent()
    queries = [
        "What is the quadratic formula?",
        "Find the derivative of x^3 - 5x.",
        "State and use the Pythagorean theorem to find the hypotenuse for legs 5 and 12.",
        "Evaluate the integral of 2x dx."
    ]
    for q in queries:
        print("="*80)
        print("Q:", q)
        res = agent.route_and_answer(q)
        print("Source:", res["source"], "| Confidence:", f"{res['confidence_score']:.3f}", "| KB matches:", res["kb_matches"])
        print("\nAnswer:\n", res["answer"], "\n")

if __name__ == "__main__":
    run()
