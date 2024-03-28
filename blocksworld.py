class Blocksworld():
    def __init__(self, initial_state, goal_state):
        self.initial_state = self.construct_state(initial_state)
        self.state = self.construct_state(initial_state)
        self.goal_state = self.construct_state(goal_state)
        self.arm = None
        self.done = False
        self.actions = []
        self.draw()

    def construct_state(self, given_state):
        state = {}
        for stack in given_state:
            state[stack[-1]] = stack
        return state

    def play_move(self, action):
        if self.done:
            print("Game already completed.")
            return False

        if action[0] == 'pickup':
            block = action[1]
            if not self.arm and block in self.state and len(self.state[block]) == 1:
                self.arm = self.state[block].pop()
                del self.state[block]
                self.actions.append(action)
            else:
                print("Invalid action.")

        elif action[0] == 'putdown':
            block = action[1]
            if self.arm == block:
                self.arm = None
                self.state[block] = [block]
                self.actions.append(action)
            else:
                print('Invalid action.')

        elif action[0] == 'unstack':
            block1, block2 = action[1], action[2]
            if not self.arm and block1 in self.state and len(self.state[block1]) > 1 and self.state[block1][-2] == block2:
                self.arm = block1
                self.state[block1].pop()
                self.state[block2] = self.state[block1]
                del self.state[block1]
                self.actions.append(action)
            else:
                print("Invalid action.")

        elif action[0] == 'stack':
            block1, block2 = action[1], action[2]
            if self.arm == block1 and block2 in self.state:
                self.arm = None
                self.state[block2].append(block1)
                self.state[block1] = self.state[block2]
                del self.state[block2]
                self.actions.append(action)
            else:
                print("Invalid action.")
        else:
            print("Invalid action.")

        if self.state == self.goal_state:
            print("Congratulations! Goal state reached.")
            self.done = True
        return True

    def draw(self):
        i = 1
        print('####################')
        print('####################')
        print()
        if self.actions:
            print('Action:', ' '.join(self.actions[-1]))

        print("Arm:", str(self.arm))
        for stack in self.state.values():
            print("Stack ", i)
            for j in range(len(stack)-1, -1, -1):
                print(stack[j])
            i += 1


initial_state = [["A", "B", "C"]]
goal_state = [["C", "A", "B"]]
game = Blocksworld(initial_state, goal_state)

actions = [("unstack", 'C', 'B'), ('putdown', 'C'), ("unstack", 'B', 'A'), ('putdown', 'B'), ('pickup', 'A'), ('stack', 'A', 'C'), ('pickup', 'B'), ('stack', 'B', 'A')]
for action in actions:
    game.play_move(action)
    game.draw()
