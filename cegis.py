class CeGIS:
    def __init__(self, world, verifier, llm):
        self.world = world
        self.verifier = verifier
        self.llm = llm
        
    def run(self):
        init_state = self.world.initial_state
        goal_state = self.world.goal_state
        counter_example = None
        solved = False
        while not solved:
            prompt = self.build_prompt(init_state, goal_state, counter_example)
            solution = self.llm.solve(prompt)
            counter_example = self.verifier.verify(prompt, solution)
            if counter_example is None:
                solved = True
    
    def build_prompt(self, init_state, goal_state, counter_example):
        pass
        