from z3 import *
from blocksworld import Blocksworld
from utils import get_all_blocks, get_clear_blocks, get_table_blocks, get_arm_block
import copy
class State:
    def __init__(self, name):
        self.table = Function(f'{name}_table', IntSort(), BoolSort())
        self.hand = Function(f'{name}_hand', IntSort(), BoolSort())
        self.stacked = Function(f'{name}_stacked', IntSort(), IntSort(), BoolSort())
        self.clear = Function(f'{name}_clear', IntSort(), BoolSort())
        self.handsfree = Function(f'{name}_handsfree', BoolSort())


def get_state_constaints(world, blockA, blockB, blockAVar, blockBVar, s1, s2):
    clear_blocks = get_clear_blocks(world.state)
    table_blocks = get_table_blocks(world.state)
    arm_block = get_arm_block(world)
    state_constraints = []
    if arm_block:
        state_constraints.append(s1.handsfree())
    if blockA in clear_blocks:
        state_constraints.append(s1.clear(blockAVar))
    else:
        state_constraints.append(Not(s1.clear(blockAVar)))
    if blockA in table_blocks:
        state_constraints.append(s1.table(blockAVar))
    else:
        state_constraints.append(Not(s1.table(blockAVar)))
    if blockA == arm_block:
        state_constraints.append(s1.hand(blockAVar))
    else:
        state_constraints.append(Not(s1.hand(blockAVar)))
    if blockB:
        if blockB in clear_blocks:
            state_constraints.append(s1.clear(blockBVar))
        else:
            state_constraints.append(Not(s1.clear(blockBVar)))
        if blockB in table_blocks:
            state_constraints.append(s1.table(blockBVar))
        else:
            state_constraints.append(Not(s1.table(blockBVar)))
        if blockB == arm_block:
            state_constraints.append(s1.hand(blockBVar))
        else:
            state_constraints.append(Not(s1.hand(blockBVar)))
        if blockA in world.state and len(world.state[blockA]) >= 2 and world.state[blockA][-2] == blockB:
            state_constraints.append(s1.stacked(blockAVar, blockBVar))
        else:
            state_constraints.append(Not(s1.stacked(blockAVar, blockBVar)))
    return state_constraints

############## pick up constraints##############
def check_pickup(world, blockA):        
    s1 = State('s1')
    s2 = State('s2')
    the_block = ord(blockA)
    state_constraints = get_state_constaints(world, blockA, None, the_block, None, s1, s2)
    constraint1 = And(s1.table(the_block), s1.clear(the_block))
    constraint2 = Not(s1.hand(the_block))
    constraints = And(*state_constraints, constraint1, constraint2)

    solver = Solver()
    solver.add(constraints)
    if solver.check() == sat: 
        return True
    else: 
        return False

def check_putdown(world, blockA):
    s1 = State('s1')
    s2 = State('s2')
    solver = Solver() # 1. The block is in the hand in state s1. 
    block = ord(blockA)
    state_constraints = get_state_constaints(world, blockA, None, block, None, s1, s2)
    constraints = []
    constraints.append(And(*state_constraints))
    constraints.append(s1.hand(block)) # 2. The block is not on the table in state s1. 
    constraints.append(Not(s1.table(block))) # 3. The block is not in the hand in state s2. 
    constraints.append(Not(s2.hand(block))) # 4. The block is on the table in state s2. 
    constraints.append(s2.table(block)) # 5. The block is clear in state s2. 
    constraints.append(s2.clear(block)) # For all other blocks x, the state of the hand, table, and clear should remain the same between s1 and s2. 
    solver.add(And(*constraints))
    if solver.check() == sat: 
        return True
    else: 
        return False

def check_stack(world, blockA, blockB):
    s1 = State('s1')
    s2 = State('s2')
    block1 = ord(blockA)
    block2 = ord(blockB)
    x = Int('x')
    y = Int('y')
    constraints = get_state_constaints(world, blockA, blockB, block1, block2, s1, s2)
    constraints.append(Or(
        And(
            # If the block1 is being stacked from the table
            s1.table(block1), # The block1 is on the table in state s1
            Not(s1.stacked(block1, block2)), # Neither block1 nor block2 are stacked on each other in state s1
            s1.clear(block1), # Block1 is clear in state s1
            s1.clear(block2), # Block2 is clear in state s1
        ),
        And(
            s1.hand(block1), # The block1 is in the agent's hand in state s1
            Not(s1.stacked(block1, block2)), # Neither block1 nor block2 are stacked on each other in state s1
            s1.clear(block2), # Block2 is clear in state s1
        )
    ))
    # If the block1 is being stacked from the hand
    all_constraints = And(*constraints)
    solver = Solver()
    solver.add(all_constraints)
    if solver.check() == sat:
        return True
    else:
        return False

def check_unstack(world, blockA, blockB):
    s1 = State('s1')
    s2 = State('s2')
    block1 = ord(blockA)
    block2 = ord(blockB)
    # x, y = Ints('x y')
    # blocks = [x, y]
    # blocks_except = [b for b in blocks if b != block1 and b != block2]
    state_constraints = get_state_constaints(world, blockA, blockB, block1, block2, s1, s2)
    unstack_to_table = And(
        s1.stacked(block1, block2),
        s1.clear(block1),
    )
    # Block unstacked to the hand
    unstack_to_hand = And(
        s1.stacked(block1, block2),
        s1.clear(block1),
        # s1.handsfree(),
        # Not(s2.stacked(block1, block2)),
        # s2.hand(block1),
        # Not(s2.clear(block1)),
        # s2.clear(block2),
        # Not(s2.handsfree())
    )
    constraints = And(*state_constraints, Or(unstack_to_table, unstack_to_hand))
    solver = Solver()
    solver.add(constraints)
    if solver.check() == sat:
        return True
    else:
        return False


class Verifier:
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state[::]
        self.goal_state = goal_state[::]

    def generate_counter_example(self, solution, idx):
        counter_example_str = ', '.join(f'{d}' for d in solution[:idx+1])
        return counter_example_str

    def verify(self, solution):
        # print('BEFOR:', self.initial_state)
        world = Blocksworld(copy.deepcopy(self.initial_state), copy.deepcopy(self.goal_state))

        SAT=True
        for idx, action in enumerate(solution):
            if action[0] == 'pickup':
                SAT = check_pickup(world, action[1])
            if action[0] == 'putdown':
                SAT = check_putdown(world, action[1])
            if action[0] == 'stack':
                SAT = check_stack(world, action[1], action[2])
            if action[0] == 'unstack':
                SAT = check_unstack(world, action[1], action[2])
            
            if not SAT:
                counter_example_str = ', '.join(f'{d}' for d in solution[:idx+1])
                return (False, counter_example_str)                 
            if SAT:
                world.play_move(action)
            
            if world.done:
                if idx != len(solution)-1:
                    return (True, 'accidental solve')
                else:
                    return (True, None)
                # world.draw()
            # print('AFTER:', self.initial_state)
        # print(SAT)
        if world.done:
            return (True, None)
        else:
            return (False, self.generate_counter_example(solution, len(solution)-1))


if __name__ == "__main__":
    initial_state = [["A", "B"]]
    goal_state = [["A", "B"]]
    ver = Verifier(initial_state, goal_state)
    solution = [
        ('unstack', 'A', 'B'),
    ]
    print(ver.verify([]))