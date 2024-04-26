from llm import LanguageModel, SYSTEM_PROMPT, OPENAI_API_KEY
from cegis import CeGIS
from blocksworld import Blocksworld
from utils import random_initial_state
from prover import Verifier
import json
from datetime import datetime
import sys
import argparse

def run_experiment(config_file, fuzzing_enabled=False):
    with open(config_file, "r") as f:
        config = json.load(f)
    exp_results = {
        'meta': config['meta']['num-blocks'],
        'results': {},
        'fuzzing': fuzzing_enabled
    }
    exp_dir = f'data/exp{config["meta"]["num-blocks"]}-{datetime.now().strftime("%Y-%m-%d-%H_%M_%S")}.json'
    for model in config["meta"]["models"]:
        exp_results['results'][model] = []
        for exp in config["experiments"]:
            print(f"Running Experiment: {exp}\nModel: {model}\nFuzzing: {fuzzing_enabled}")
            initial_state = exp["initial"]
            goal_state = exp["goal"]
            model_type = model
            verifier = Verifier(initial_state, goal_state)
            LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT, model_type)
            cegis = CeGIS(verifier, LLM, fuzzing_enabled)
            solved, iters = cegis.run()
            exp_results['results'][model].append({
                "solved": solved,
                "iters": iters
            })
    with open(exp_dir, "w") as f:
        json.dump(exp_results, f)
        

def parse_args():
    parser = argparse.ArgumentParser(description='Run experiments')
    parser.add_argument('config', type=str, help='config file')
    parser.add_argument('--fuzzing', action='store_true', help='enable fuzzing')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # initial_state = [["A"], ["B"], ["C"], ["D"]]
    # goal_state = [["A", "B", "C", "D"]]
    # model_type="gpt-4-turbo-preview"
    # # model_type="gpt-3.5-turbo"
    # verifier = Verifier(initial_state, goal_state)
    # LLM = LanguageModel(OPENAI_API_KEY, SYSTEM_PROMPT, model_type)
    # cegis = CeGIS(verifier, LLM)
    # cegis.run()
    # config_file = "config/auto-exp-3.json"
    # config_file = "config/exp-3.json"
    args = parse_args()
    # args = sys.argv
    # if len(args) > 1:
    #     config_file = f"config/exp-{args[1]}.json"
    run_experiment(args.config, fuzzing_enabled=args.fuzzing)
