class CeGIS:
    def __init__(self, initial_state, goal_state, verifier, llm):
        self.verifier = verifier
        self.llm = llm
        self.initial_state = initial_state
        self.goal_state = goal_state
        
    def run(self):
        init_state = self.initial_state
        goal_state = self.goal_state
        counter_example = None
        solved = False
        while not solved:
            prompt = self.build_prompt(init_state, goal_state, counter_example)
            solution = self.llm.solve(prompt)

            print("Actions:", solution)
            solved, counter_example = self.verifier.verify(solution)
            # if solved:
            #     counter_example = solution
    
    def build_prompt(self, init_state, goal_state, counter_example):
        prompt = f"input: {init_state}\noutput: {goal_state}.\nResult:"
        if counter_example:
            # play around with prefix/full solution
            counter_prompt = counter_example + "Any plan with the above prefix is not correct. Try again."
            prompt = counter_prompt + prompt
        return prompt
