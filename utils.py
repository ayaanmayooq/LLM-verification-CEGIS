from blocksworld import Blocksworld
import random


def get_clear_blocks(state):
    return [k for k in state if len(state[k]) != 1]


def get_table_blocks(state):
    return [k for k in state if len(state[k]) == 1]


def get_all_blocks(world):
    arm = [world.arm] if world.arm else []
    blocks = []
    for k in world.state:
        blocks += world.state[k]
    return blocks + arm


def get_random_action(world):
    state = world.state
    available_actions = Blocksworld._actions[::]
    # filter out invalid actions
    if not world.arm:
        available_actions.remove("putdown")
        available_actions.remove("stack")
    clear_blocks = get_clear_blocks(state)
    table_blocks = get_table_blocks(state)
    if len(clear_blocks) == 0 or world.arm:
        available_actions.remove("unstack")
    if len(table_blocks) == 0 or world.arm:
        available_actions.remove("pickup")
    # then we select and build a random action
    action = random.choice(available_actions)
    if action == "pickup":
        block = random.choice(clear_blocks + table_blocks)
        return ("pickup", block)
    elif action == "putdown":
        return ("putdown", world.arm)
    elif action == "unstack":
        block1 = random.choice(clear_blocks)
        block2 = state[block1][-2]
        return ("unstack", block1, block2)
    elif action == "stack":
        block1 = world.arm
        block2 = random.choice(clear_blocks + table_blocks)
        return ("stack", block1, block2)


def random_initial_state(num_blocks=5, num_stacks=2):
    if num_blocks < num_stacks:
        raise ValueError("Number of blocks should be greater than number of stacks.")
    blocks = []
    for i in range(num_blocks):
        blocks.append(chr(65 + i))
    split_points = random.sample(range(1, num_blocks), num_stacks - 1)
    split_points.sort()
    split_points = [0] + split_points + [num_blocks]
    print(split_points)
    stacks = []
    for i in range(num_stacks):
        stacks.append(blocks[split_points[i] : split_points[i + 1]])
    return stacks


if __name__ == "__main__":
    NUM_BLOCKS = 5
    NUM_STACKS = 2
    initial_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    print(initial_state)
    goal_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    while initial_state == goal_state:
        goal_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    world = Blocksworld(initial_state, goal_state)
    world.draw()
    while not world.done:
        action = get_random_action(world)
        print(f"random actions: {action}")
        world.play_move(action)
        world.draw()
    print(world.actions)
    print(world.state)
    print(world.goal_state)
