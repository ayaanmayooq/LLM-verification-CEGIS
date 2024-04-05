import pygame
import pygame.gfxdraw
from blocksworld import Blocksworld
from utils import get_all_blocks
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
    def __init__(self, x, y, label='A', size=50):
        self.x = x
        self.y = y
        self.label = label
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_MAP[self.label], (self.x, self.y, self.size, self.size))
        font = pygame.font.Font(None, 36)
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x+self.size//2, self.y+self.size//2))
        screen.blit(text, text_rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Button:
    def __init__(self, x, y, label='A', width=50, height=25):
        self.x = x
        self.y = y
        self.label = label
        self.width = width
        self.height = height
        self.clicked = False
        self.clicked_color = (255, 0, 0)
        self.uncliked_color = (0, 0, 0)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def color(self):
        return self.clicked_color if self.clicked else self.uncliked_color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 18)
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x+self.width//2, self.y+self.height//2))
        screen.blit(text, text_rect)

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = not self.clicked
            return True
        return False

def get_controls(world):
    blocks = get_all_blocks(world)
    actions = Blocksworld._actions
    action_buttons=[]
    # draw button actions
    for idx, action in enumerate(actions):
        button = Button(50+idx*125, 50, label=action, width=75, height=25)
        action_buttons.append(button)
    # draw blocks
    block_buttons=[]
    for idx, block in enumerate(blocks):
        button = Button(50+idx*90, 100, label=block, width=35, height=35)
        block_buttons.append(button)
        
    enter_button = Button(50, 150, label="Enter", width=50, height=25)
    return action_buttons, block_buttons, enter_button

def draw_rect_outline(surface, rect, color, width=1):
    x, y, w, h = rect
    width = max(width, 1)  
    width = min(min(width, w//2), h//2)  
    for i in range(width):
        pygame.gfxdraw.rectangle(screen, (x+i, y+i, w-i*2, h-i*2), color)

def draw_controls(screen, action_buttons, block_buttons, enter_button):
    control_rect = pygame.Rect(0, 0, 600, 200)
    draw_rect_outline(screen, control_rect, (0, 0, 0), 2)
    for button in action_buttons:
        button.draw(screen)
    for button in block_buttons:
        button.draw(screen)
    enter_button.draw(screen)

def get_action_stack(action_buttons, action_stack, pos):
    for button in action_buttons:
        if button.click(pos):
            if button.clicked:
                action_stack.append(button.label)
            else:
                action_stack.remove(button.label)
    return None

def get_block_stack(block_buttons, block_stack, pos): 
    for button in block_buttons:
        if button.click(pos):
            if button.clicked:
                block_stack.append(button.label)
            else:
                block_stack.remove(button.label)
    return None

def check_enter(action_stack, block_stack, enter_button, pos):
    clicked_enter = enter_button.click(pos)
    if clicked_enter:
        for b in block_buttons+action_buttons+[enter_button]:
            b.clicked = False
        if len(action_stack) and len(block_stack):
            a=(action_stack[0],)
            b=(block_stack[0], block_stack[1]) if len(block_stack) > 1 else (block_stack[0],)
            return a+b
    return None

def draw_current_action(screen, action_stack, block_stack):
    text = ",".join([f'"{x}"' for x in action_stack+block_stack])
    font = pygame.font.Font(None, 24)
    text = font.render(f"Action: ({text})", True, (0, 0, 0))
    text_rect = text.get_rect(topleft=(50, 20))
    screen.blit(text, text_rect)

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
    action_buttons, block_buttons, enter_button = get_controls(world)
    buttons = action_buttons + block_buttons + [enter_button]
    # pos = (-1, -1)
    running = True
    action_stack = []
    block_stack = []
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if len(actions) > 0:
                    world.play_move(actions.pop(0))
                    world.draw()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                action = get_action_stack(action_buttons, action_stack,pos)
                block = get_block_stack(block_buttons,block_stack, pos)
                enter_action = check_enter(action_stack, block_stack, enter_button, pos)
                if enter_action:
                    print(enter_action)
                    action_stack = []
                    block_stack = []
                    try:
                        world.play_move(enter_action)
                        world.draw()
                    except:
                        print("Invalid action.")
        render(screen, world)
        draw_controls(screen, action_buttons, block_buttons, enter_button)
        draw_current_action(screen, action_stack, block_stack)
        pygame.display.flip()
    pygame.quit()
