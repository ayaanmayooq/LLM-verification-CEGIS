import json
from datetime import datetime
import os
import sys

class CeGIS:
    def __init__(self, verifier, llm):
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
        self.PREF_MODE = True
        
    def run(self):
        counter_example = None
        solved = False
        print(f'Problem Statement:\nInitial:{self.initial_state}\nGoal:{self.goal_state}')
        TRY_NUM=0
        MAX_TRIES=50
        while not solved:
            print(f'[ITER-{TRY_NUM}]======================================')
            prompt = self.build_prompt(self.initial_state, self.goal_state, counter_example)
            print(f"LLM Prompt:\n```\n{prompt}\n```")
            solution = self.llm.solve(prompt)
            if not solution:
                solution = []
            print(f'[ITER-{TRY_NUM}] LLM Response: {solution}')
            try:
                solved, counter_example = self.verifier.verify(solution)
            except:
                solved, counter_example = False, None
            if not solved and not self.PREF_MODE:
                counter_example = solution
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
            self.log_data['stats']['iters']=len(self.log_data['results'])
            self.log_data['stats']['solved']=solved
            # self.dump_logs()
            if solved:
                print('SOLUTION HAS BEEN FOUND 🎉')
                break
            TRY_NUM+=1
            if TRY_NUM >= MAX_TRIES:
                break
        print(f'[LOG] Experiment Completed. Logs written to {self.exp_dir}')
        return (solved, TRY_NUM)
    
    
    def build_prompt(self, init_state, goal_state, counter_example):
        prompt = f"Try again.\ninitial state: {init_state}\ngoal state: {goal_state}.\nAnswer:"
        if counter_example:
            # play around with prefix/full solution
            if self.PREF_MODE:
                counter_prompt =f"\nAny plan with the following prefix is not correct.\n{counter_example}\nTry again.\n"
            else: 
                counter_prompt = f"\nYour previous solution DID NOT WORK. This is your previous attempt```\n{counter_example}\n```\nYOU MUST TRY A DIFFERENT SOLUTION.\n"
            prompt = counter_prompt + prompt
        return prompt

    def dump_logs(self):
        with open(self.exp_dir, 'w') as fo:
            json.dump(self.log_data, fo)
            # print(f'[LOG] Wrote logs to {self.exp_dir}')