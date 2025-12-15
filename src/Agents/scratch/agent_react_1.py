# react_agent.py
import re
from typing import Callable, Dict, Optional, Any

# -----------------------------
# 1) Tools (real Python functions)
# -----------------------------
def calculate(operation: str) -> float:
    """
    NOTE: eval is risky. For learning it's okay.
    For safer use, replace with a proper math parser.
    """
    return eval(operation, {"__builtins__": {}})

def get_planet_mass(planet: str) -> Optional[float]:
    planet = planet.strip().lower()
    masses = {
        "earth": 5.972e24,
        "mars": 6.39e23,
        "jupiter": 1.898e27,
        "saturn": 5.683e26,
        "uranus": 8.681e25,
        "neptune": 1.024e26,
        "mercury": 3.285e23,
        "venus": 4.867e24,
    }
    return masses.get(planet)

# -----------------------------
# 2) System prompt (ReAct protocol)
# -----------------------------
system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth
Action: get_planet_mass: Earth
PAUSE

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this:

Observation: 1.1944e25

If you have the answer, output it as the Answer.

Now it's your turn:
""".strip()

# -----------------------------
# 3) Agent class (callable object via __call__)
# -----------------------------
class Agent:
    def __init__(self, client: Any, system: Optional[str]):
        self.client = client
        self.system = system
        self.messages = []
        if self.system is not None:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message: str) -> str:
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
        # IMPORTANT: use self.client (not a global "client")
        completion = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=self.messages,
        )
        return completion.choices[0].message.content

# -----------------------------
# 4) Action parsing + tool dispatch
# -----------------------------
ACTION_PATTERN = re.compile(r"Action:\s*([a-z_]+)\s*:\s*(.+)", re.IGNORECASE)

def parse_action(text: str) -> Optional[tuple[str, str]]:
    """
    Returns (tool_name, arg) if an Action line exists, else None.
    """
    match = ACTION_PATTERN.search(text)
    if not match:
        return None
    tool_name = match.group(1).strip().lower()
    arg = match.group(2).strip()
    return tool_name, arg

def run_tool(tool_name: str, arg: str, tool_map: Dict[str, Callable[[str], Any]]) -> Any:
    """
    Executes a whitelisted tool safely (no eval).
    """
    if tool_name not in tool_map:
        raise ValueError(f"Tool not found: {tool_name}")
    return tool_map[tool_name](arg)

# -----------------------------
# 5) The ReAct loop orchestrator
# -----------------------------
def loop(client: Any, query: str, max_iterations: int = 10) -> str:
    agent = Agent(client=client, system=system_prompt)

    tool_map: Dict[str, Callable[[str], Any]] = {
        "calculate": calculate,
        "get_planet_mass": get_planet_mass,
    }

    next_prompt = query

    for step in range(1, max_iterations + 1):
        result = agent(next_prompt)
        print(f"\n--- Step {step} ---")
        print(result)

        # If model asked for a tool
        if ("PAUSE" in result) and ("Action" in result):
            parsed = parse_action(result)
            if not parsed:
                next_prompt = "Observation: Could not parse Action line. Please follow: Action: tool_name: argument"
                print(next_prompt)
                continue

            tool_name, arg = parsed

            try:
                tool_result = run_tool(tool_name, arg, tool_map)
                next_prompt = f"Observation: {tool_result}"
            except Exception as e:
                next_prompt = f"Observation: Tool error - {type(e).__name__}: {e}"

            print(next_prompt)
            continue

        # If model produced final answer
        if "Answer" in result:
            return result

        # Otherwise, nudge it to continue cleanly
        next_prompt = "Continue. If you need a tool, respond with Action: <tool>: <arg> then PAUSE. Otherwise give Answer."

    return "Answer: Reached max iterations without a final Answer."

# -----------------------------
# 6) Example usage
# -----------------------------
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    from groq import Groq

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found in environment/.env")

    client = Groq(api_key=api_key)

    output = loop(
        client=client,
        query="What is the mass of Earth plus the mass of Saturn and all of that times 2?"
    )
    print("\nFINAL OUTPUT:\n", output)
