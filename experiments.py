from llm import LanguageModel, SYSTEM_PROMPT, OPENAI_API_KEY
from cegis import CeGIS
from blocksworld import Blocksworld
from utils import random_initial_state
from prover import Verifier

if __name__ == "__main__":
    initial_state = [["A"], ["B", "C"]]
    goal_state = [["C", "A", "B"]]

    verifier = Verifier(initial_state, goal_state)
    LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT)
    cegis = CeGIS(initial_state, goal_state, verifier, LLM)

    cegis.run()
