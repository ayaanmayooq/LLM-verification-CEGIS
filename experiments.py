from llm import LanguageModel, SYSTEM_PROMPT, OPENAI_API_KEY
from cegis import CeGIS
from blocksworld import Blocksworld
from utils import random_initial_state
from prover import Verifier
import json
from datetime import datetime

def run_experiment(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    exp_results = {
        'meta': config['meta']['num-blocks'],
        'results': {},
    }
    exp_dir = f'data/exp{config["meta"]["num-blocks"]}-{datetime.now().strftime("%Y-%m-%d-%H_%M_%S")}.json'
    for model in config["meta"]["models"]:
        exp_results['results'][model] = []
        for exp in config["experiments"]:
            print(f"Running Experiment: {exp}")
            initial_state = exp["initial"]
            goal_state = exp["goal"]
            model_type = model
            verifier = Verifier(initial_state, goal_state)
            LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT, model_type)
            cegis = CeGIS(verifier, LLM)
            solved, iters = cegis.run()
            exp_results['results'][model].append({
                "solved": solved,
                "iters": iters
            })
    with open(exp_dir, "w") as f:
        json.dump(exp_results, f)
        

if __name__ == "__main__":
    # initial_state = [["A"], ["B"], ["C"], ["D"]]
    # goal_state = [["A", "B", "C", "D"]]
    # model_type="gpt-4-turbo-preview"
    # # model_type="gpt-3.5-turbo"
    # verifier = Verifier(initial_state, goal_state)
    # LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT, model_type)
    # cegis = CeGIS(verifier, LLM)
    # cegis.run()
    config_file = "config/exp.json"
    run_experiment(config_file)
