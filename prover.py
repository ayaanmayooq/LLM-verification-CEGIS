from z3 import *
from blocksworld import Blocksworld
from utils import get_all_blocks, get_clear_blocks, get_table_blocks, get_arm_block

class State:
    def __init__(self, name):
        self.table = Function(f'{name}_table', IntSort(), BoolSort())
        self.hand = Function(f'{name}_hand', IntSort(), BoolSort())
        self.stacked = Function(f'{name}_stacked', IntSort(), IntSort(), BoolSort())
        self.clear = Function(f'{name}_clear', IntSort(), BoolSort())
        self.handsfree = Function(f'{name}_handsfree', BoolSort())

# here we need to extract z3 specs from current state, then add to our constraints
# if x is not clear but pickup states it is clear, we will have a contradiction
# clear blocks
# table blocks
# arm blocks
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
    # constraint3 = s2.hand(the_block)
    # constraint4 = And(Not(s2.table(the_block)), Not(s2.clear(the_block)))
    # x = Int('x')
    # fun = Function('fun', IntSort(), BoolSort())
    # constraint5 = ForAll([x], Implies(x != the_block, And(s1.table(x) == s2.table(x), s1.hand(x) == s2.hand(x), s1.clear(x) == s2.clear(x))))
    # x = Int('x')
    # y = Int('y')
    # constraint6 = ForAll([x, y], s1.stacked(x, y) == s2.stacked(x, y))
    constraints = And(*state_constraints, constraint1, constraint2)

    solver = Solver()
    solver.add(constraints)
    if solver.check() == sat: 
        print(solver.model()) 
        return True
    else: 
        print("No solution found")
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
    # x = Int('x') 
    # constraints.append(ForAll([x], And(x != block, s1.hand(x) == s2.hand(x), s1.table(x) == s2.table(x), s1.clear(x) == s2.clear(x)))) # For all blocks x, y, the state of the stacked should remain the same between s1 and s2. 
    # x = Int('x') 
    # y = Int('y') 
    # constraints.append(ForAll([x, y], s1.stacked(x, y) == s2.stacked(x, y))) # Check the constraints and print the result 
    solver.add(And(*constraints))
    if solver.check() == sat: 
        # print(solver.model()) 
        return True
    else: 
        print("No solution found")
        return False

def check_stack(world, blockA, blockB):
    s1 = State('s1')
    s2 = State('s2')
    block1 = ord(blockA)
    block2 = ord(blockB)
    x = Int('x')
    y = Int('y')
    constraints = get_state_constaints(world, blockA, blockB, block1, block2, s1, s2)
    # print(constraints)
    # For all blocks x other than these two blocks, the state of the hand, table, and clear should remain the same between the states s1 and s2
    # constraints.append(ForAll(x, Implies(And(x != block1, x != block2), And(s1.hand(x) ==
    # s2.hand(x), s1.table(x) == s2.table(x), s1.clear(x) == s2.clear(x)))))
    # # For all blocks x, y, where neither x is block1, nor y is block2, the state of being stacked should remain the same between s1 and s2
    # constraints.append(ForAll([x, y], Implies(And(x != block1, y != block2), s1.stacked(x, y) == s2.stacked(x, y))))
    # The block is either stacked from the table or from the hand
    constraints.append(Or(
        And(
            # If the block1 is being stacked from the table
            s1.table(block1), # The block1 is on the table in state s1
            Not(s1.stacked(block1, block2)), # Neither block1 nor block2 are stacked on each other in state s1
            s1.clear(block1), # Block1 is clear in state s1
            s1.clear(block2), # Block2 is clear in state s1
            # s1.handsfree(), # The agent's hand is free in state s1
            # Not(s2.table(block1)), # Block1 is not on the table in state s2
            # Not(s2.hand(block1)), # Block1 is not in the agent's hand in state s2
            # s2.stacked(block1, block2), # Block1 is stacked on block2 in state s2
            # s2.clear(block1), # Block1 is clear in state s2
            # Not(s2.clear(block2)), # Block2 is not clear in state s2
        ),
        And(
            s1.hand(block1), # The block1 is in the agent's hand in state s1
            Not(s1.stacked(block1, block2)), # Neither block1 nor block2 are stacked on each other in state s1
            s1.clear(block2), # Block2 is clear in state s1
            # # Not(s1.handsfree()), # The agent's hand is not free in state s1
            # Not(s2.table(block1)), # Block1 is not on the table in state s2
            # Not(s2.hand(block1)), # Block1 is not in the agent's hand in state s2
            # s2.stacked(block1, block2), # Block1 is stacked on block2 in state s2
            # s2.clear(block1), # Block1 is clear in state s2
            # Not(s2.clear(block2)), # Block2 is not clear in state s2
        )
    ))
    # If the block1 is being stacked from the hand
    print(constraints)
    all_constraints = And(*constraints)
    solver = Solver()
    solver.add(all_constraints)
    if solver.check() == sat:
        # print(solver.model())
        return True
    else:
        print("No solution found")
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
    # Invariants for all blocks
    # invariants = And(
    #     ForAll([x], Implies(x != block1, And(s1.table(x) == s2.table(x), s1.hand(x) == s2.hand(x),
    #     s1.clear(x) == s2.clear(x)))),
    #     ForAll([x], Implies(x != block2, And(s1.table(x) == s2.table(x), s1.hand(x) == s2.hand(x),
    #     s1.clear(x) == s2.clear(x)))),
    #     ForAll([x, y], Implies(And(x != block1, y != block2), s1.stacked(x, y) == s2.stacked(x, y))),
    # )
    # Block unstacked to the table
    unstack_to_table = And(
        s1.stacked(block1, block2),
        s1.clear(block1),
        # s1.handsfree(),
        # Not(s2.stacked(block1, block2)),
        # s2.table(block1),
        # s2.clear(block1),
        # s2.clear(block2),
        # s2.handsfree()
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
        # print(solver.model())
        return True
    else:
        print("No solution found")
        return False


class Verifier:
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state[::]
        self.goal_state = goal_state[::]

    def verify(self, solution):
        print(self.initial_state)
        world = Blocksworld(self.initial_state[::], self.goal_state[::])

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
                print("Solution has not been found")
                world.draw()
                print(action)

                counter_example_str = ', '.join(f'{d}' for d in solution[:idx+1])
                return (False, counter_example_str)                 
            if SAT:
                world.play_move(action)
                world.draw()
            # game.play_move(action)
            # game.draw()
        return (True, None)


if __name__ == "__main__":
    # initial_state = [["A", "B", "C"]]
    # goal_state = [["C", "A", "B"]]
    # world = Blocksworld(initial_state, goal_state)
    # # # check_pickup(world, 'A')
    # # # check_putdown(world, 'A')
    # check_unstack(world, 'C', 'B')
    # world.play_move(('unstack', 'C', 'B'))
    # check_stack(world, 'C', 'B')
    ver = Verifier()
    solution = [
        ('unstack', 'C', 'B'),
        ('putdown', 'C'),
        ('unstack', 'B', 'A'),
        ('putdown', 'B'),
        ('pickup', 'A'),
        ('stack', 'A', 'C'),
        ('pickup', 'B'),
        ('stack', 'B', 'A')
    ]
    print(ver.verify(solution))