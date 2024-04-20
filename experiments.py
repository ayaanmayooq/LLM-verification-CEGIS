import llm
from llm import LanguageModel, SYSTEM_PROMPT, OPENAI_API_KEY
from cegis import CeGIS
from blocksworld import Blocksworld
from utils import random_initial_state
# from prover import Verifier

if __name__ == "__main__":
    initial_state = random_initial_state(num_blocks=5, num_stacks=2)
    goal_state = [['A', 'B', 'C', 'D', 'E']]

    world = Blocksworld(initial_state, goal_state)
    # verifier = Verifier()
    LLM = llm.LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT)
    # cegis = CeGIS(world, verifier, LLM)
