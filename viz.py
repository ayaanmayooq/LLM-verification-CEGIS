import pygame
from blocksworld import Blocksworld
# GLOBALS
BLOCK_SIZE=50
SCREEN_WIDTH=800
SCREEN_HEIGHT=600
CENTER = SCREEN_WIDTH // 2
NUM_STACKS = 5
HALF_WIDTH_STACKS = NUM_STACKS // 2
STACK_RANGE = range(-HALF_WIDTH_STACKS, HALF_WIDTH_STACKS)
STACK_X_POS = [CENTER+(2*i*BLOCK_SIZE) for i in STACK_RANGE]
COLOR_MAP={
    "A": (255, 0, 0),
    "B": (0, 255, 0),
    "C": (0, 0, 255),
    "D": (255, 255, 0),
    "E": (0, 255, 255),
    "F": (255, 0, 255),
    "G": (255, 255, 255),
    "H": (128, 128, 128),
}

# block object
class Block:
    def __init__(self, x, y, label='A'):
        self.x = x
        self.y = y
        self.label = label

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_MAP[self.label], (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x+BLOCK_SIZE//2, self.y+BLOCK_SIZE//2))
        screen.blit(text, text_rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# main render func
def render(screen, world):
    # draw stacks
    for idx, val in enumerate(world.order):
        stack= world.state[val] if len(val) else []
        for j in range(len(stack)):
            block = Block(STACK_X_POS[idx], -20+SCREEN_HEIGHT - (j+1)*BLOCK_SIZE, stack[j])
            block.draw(screen)
    # draw table
    pygame.draw.rect(screen, (0, 0, 0), (0, SCREEN_HEIGHT-20, SCREEN_WIDTH, 20))
    # draw info
    arm_x,arm_y = CENTER, 300+BLOCK_SIZE//2
    font = pygame.font.Font(None, 36)
    text = font.render("Arm:", True, (0, 0, 0))
    text_rect = text.get_rect(center=(arm_x, arm_y))
    screen.blit(text, text_rect)
    font = pygame.font.Font(None, 48)
    text = font.render("Press any key to step forward", True, (0, 0, 0))
    text_rect = text.get_rect(center=(CENTER, BLOCK_SIZE//2))
    screen.blit(text, text_rect)
    if world.arm:
        x,y = CENTER+BLOCK_SIZE, 300+BLOCK_SIZE//4
        block = Block(x, y, world.arm)
        block.draw(screen)
     
        

if __name__ == '__main__':
    initial_state = [["A", "B", "C"]]
    goal_state = [["C", "A", "B"]]
    world = Blocksworld(initial_state, goal_state)
    actions = [("unstack", 'C', 'B'), ('putdown', 'C'), ("unstack", 'B', 'A'), ('putdown', 'B'), ('pickup', 'A'), ('stack', 'A', 'C'), ('pickup', 'B'), ('stack', 'B', 'A')]

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((255, 255, 255))
    pygame.display.flip()
    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if len(actions) > 0:
                    world.play_move(actions.pop(0))
                    world.draw()
        render(screen, world)
        pygame.display.flip()
    pygame.quit()
