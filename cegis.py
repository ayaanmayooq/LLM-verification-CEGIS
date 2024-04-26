import json
from datetime import datetime
import os
import sys
import tqdm
import random

class CeGIS:
    def __init__(self, verifier, llm, fuzzing_enabled=False):
        self.verifier = verifier
        self.llm = llm
        self.initial_state = verifier.initial_state
        self.goal_state = verifier.goal_state
        self.num_blocks = len([a for j in self.initial_state for a in j])
        self.exp_dir = f'data/{datetime.now().strftime("%Y-%m-%d-%H_%M_%S")}-NUM{self.num_blocks}.json'
        self.log_data = {
            'meta': {
                'inital-state': self.initial_state,
                'goal-state': self.goal_state,
                'num-blocks': self.num_blocks,
                'model_type': self.llm.model_type,
            },
            'results': [],
            'stats': {}
        }
        self.PREF_MODE = False
        self.logging_enabled = False
        self.fuzzing_enabled = fuzzing_enabled
        
    def run(self):
        counter_example = None
        solved = False
        print(f'Problem Statement:\nInitial:{self.initial_state}\nGoal:{self.goal_state}')
        TRY_NUM = 0
        MAX_TRIES = 15
        iter_loop = tqdm.tqdm(range(MAX_TRIES))
        for _ in iter_loop:
            prompt = self.build_prompt(self.initial_state, self.goal_state, counter_example)
            solution = self.llm.solve(prompt)
            if not solution: solution = []
            try:
                solved, counter_example = self.verifier.verify(solution)
                if not self.PREF_MODE:
                    counter_example = solution
                if not solved:
                    solved = self.fuzz_and_verify(solution)
                    if solved:
                        print('SOLUTION HAS BEEN FOUND 🎉')
                        break
            except Exception as e:
                print(f'Error: {e}')
                solved, counter_example = False, solution
            TRY_NUM += 1
            if self.logging_enabled:
                self.log_iteration(TRY_NUM, prompt, solution, solved, counter_example)
            if solved:
                print('SOLUTION HAS BEEN FOUND 🎉')
                break
            if TRY_NUM >= MAX_TRIES:
                break
        return (solved, TRY_NUM)

    def fuzz_and_verify(self, solution):
        for k in range(50):
            new_solution = self.fuzzer(solution)
            # print(f'Fuzzed Solution: {new_solution}')
            solved, _ = self.verifier.verify(new_solution)
            if solved:
                return True
        return False

    def log_iteration(self, TRY_NUM, prompt, solution, solved, counter_example):
        print(f'[ITER-{TRY_NUM}]======================================')
        print(f"LLM Prompt:\n```\n{prompt}\n```")
        print(f'[ITER-{TRY_NUM}] LLM Response: {solution}')
        print(f'[ITER-{TRY_NUM}] Verify Output:\nsolved: {solved}\nCE: {counter_example}')
        print(f'====================================================')
        log_obj = {
            'iter': TRY_NUM,
            'prompt': prompt,
            'response': solution,
            'SAT': solved,
            'counterexample': counter_example
        }
        self.log_data['results'].append(log_obj)
        self.log_data['stats']['iters'] = len(self.log_data['results'])
        self.log_data['stats']['solved'] = solved
    
    
    def build_prompt(self, init_state, goal_state, counter_example):
        prompt = f"Try again.\ninitial state: {init_state}\ngoal state: {goal_state}.\nAnswer:"
        if counter_example:
            # play around with prefix/full solution
            if self.PREF_MODE:
                counter_prompt =f"Any plan with the following prefix is not correct.\n{counter_example}\nTry again.\n"
            else: 
                counter_prompt = f"Your previous solution DID NOT WORK. This is your previous attempt\n```\n{counter_example}\n```\nYOU MUST TRY A DIFFERENT SOLUTION.\n"
            prompt = counter_prompt + prompt
        return prompt

    def dump_logs(self):
        with open(self.exp_dir, 'w') as fo:
            json.dump(self.log_data, fo)
            # print(f'[LOG] Wrote logs to {self.exp_dir}')
    
    def fuzzer(self, solution):
        fuzzed_solution = []
        available_blocks = [a for j in self.initial_state for a in j]
        for action in solution:
            if random.random() > 0.5:
                fuzzed_solution.append(action)
            else:
                new_action = list(action)
                if action[0] == 'pickup':
                    new_action[1] = random.choice(available_blocks)
                elif action[0] == 'putdown':
                    pass
                elif action[0] == 'stack':
                    tmp = new_action[2]
                    new_action[2] = new_action[1]
                    new_action[1] = tmp
                elif action[0] == 'unstack':
                    tmp = new_action[2]
                    new_action[2] = new_action[1]
                    new_action[1] = tmp
                fuzzed_solution.append(tuple(new_action))
        if random.random() > 0.8:
            random.shuffle(fuzzed_solution)
        return fuzzed_solution
    
