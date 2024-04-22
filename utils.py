import json
import pandas
from blocksworld import Blocksworld
import random
import os
import seaborn as sns
import matplotlib.pyplot as plt

def get_arm_block(world):
    return world.arm if world.arm else None

def get_clear_blocks(state):
    return [k for k in state if len(state[k])]


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


def get_exp_data():
    DATA_PATH = './data'
    dir = os.listdir(DATA_PATH)
    df = pandas.DataFrame(columns=["nblocks", "model", "acc", "iters"])

    for file in dir:
        if file.startswith('exp'):
            with open(os.path.join(DATA_PATH, file), 'r') as f:
                data = json.load(f)
                results = data['results']
                for model in results:
                    acc = 0
                    for expi in results[model]:
                        if expi['solved']:
                            acc += 1

                    # if data["meta"] in df["nblocks"].tolist() and model in df["model"].tolist():
                    #     df.loc[(df["nblocks"] == data["meta"]) & (df["model"] == model), "acc"] += acc
                    # else:
                    df = df._append({"nblocks": data["meta"], 'model': model, "acc": acc / len(results[model])}, ignore_index=True)

    df = df.groupby(['nblocks', 'model']).mean()

    return df


def experiments_barplot(df):
    colors = ['#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB']
    sns.barplot(data=df, x='nblocks', y='acc', hue='model', palette=colors)
    plt.show()


if __name__ == "__main__":
    NUM_BLOCKS = 5
    NUM_STACKS = 2
    # initial_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    # print(initial_state)
    # goal_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    # while initial_state == goal_state:
    #     goal_state = random_initial_state(NUM_BLOCKS, NUM_STACKS)
    # world = Blocksworld(initial_state, goal_state)
    # world.draw()
    # while not world.done:
    #     action = get_random_action(world)
    #     print(f"random actions: {action}")
    #     world.play_move(action)
    #     world.draw()
    # print(world.actions)
    # print(world.state)
    # print(world.goal_state)
    df = get_exp_data()
    experiments_barplot(df)
