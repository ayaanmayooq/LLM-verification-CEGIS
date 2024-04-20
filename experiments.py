from llm import LanguageModel, SYSTEM_PROMPT, OPENAI_API_KEY
from cegis import CeGIS
from blocksworld import Blocksworld
from utils import random_initial_state
from prover import Verifier

if __name__ == "__main__":
    initial_state = [["A"], ["B"], ["C"], ["D"]]
    goal_state = [["A", "B", "C", "D"]]
    model_type="gpt-4-turbo-preview"
    # model_type="gpt-3.5-turbo"
    verifier = Verifier(initial_state, goal_state)
    LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT, model_type)
    cegis = CeGIS(verifier, LLM)

    cegis.run()
