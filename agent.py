from enum import Enum
import sys
import time
import random
import pyray as rl

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    context = SimulationContext()
    model = sys.argv[1]
    if model == '1':
        context.state = Mk1State()
        context.step_proc = mk1_step_world
        context.draw_proc = mk1_draw_world
    elif model == '2':
        print('not finished yet')
        return
        
        context.state = Mk2State()
        context.step_proc = mk2_step_world
        context.draw_proc = mk2_draw_world
    elif model == '3':
        print('not implemented yet')
        return
    elif model == '4':
        print('not implemented yet')
        return
    else:
        print_usage()
        return
    
    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'ロボット')
    rl.set_target_fps(TARGET_FPS) # TODO(cya): change to 60 and do manual sleep
    
    while not rl.window_should_close():
        context.step_proc(context.state)
        if not context.state.running:
            break
        
        rl.begin_drawing()
        context.draw_proc(context.state)
        rl.end_drawing()
        
    rl.close_window()
    
# Mk1 model
def mk1_draw_world(state):
    rl.clear_background(rl.BLACK)
    draw_colored_cell(state.position.x, state.position.y, rl.PINK)
    
def mk1_step_world(state):
    if not state.running:
        state.position = pick_random_position()
        state.direction = Direction.UP
        state.running = True
    
    next_position = mk1_move_robot(state)
    while will_collide(next_position):
        if state.direction == Direction.LEFT:
            state.running = False
            break
        
        state.direction = rotate_robot_clockwise(state)
        next_position = mk1_move_robot(state)
    
        
    state.position = next_position

def mk1_move_robot(state):
    next_position = Position(state.position.x, state.position.y)
    if state.direction == Direction.UP:
        next_position.y -= 1
    elif state.direction == Direction.RIGHT:
        next_position.x += 1
    elif state.direction == Direction.DOWN:
        next_position.y += 1
    elif state.direction == Direction.LEFT:
        next_position.x -= 1

    return next_position

class Mk1State:
    def __init__(self):
        self.position = None
        self.direction = None
        self.running = False

def mk2_draw_world(state):
    for i, row in enumerate(state.footprint):
        for j, col in enumerate(state.footprint[i]):
            if col == True:
                draw_colored_cell(i, j, rl.BLUE)
    
def mk2_step_world(state):
    if not state.running:
        state.footprint = make_filled_grid(False)
        state.position = pick_random_position()
        state.footprint[state.position.x, state.position.y] = True
        state.running = True

    # pick direction now
    

class Mk2State:
    def __init__(self):
        self.position = None
        self.direction = None
        self.running = False
        self.footprint = None
        
# Generic stuff        
def make_filled_grid(value):
    return [[value for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]

def draw_colored_cell(x, y, color):
    rl.draw_rectangle(
        x * PIXEL_SCALE,
        y * PIXEL_SCALE,
        PIXEL_SCALE,
        PIXEL_SCALE,
        color
    )
    
def pick_random_position():
    return Position(
        random.randint(0, MAX_X),
        random.randint(0, MAX_Y)
    )
    
def rotate_robot_clockwise(state):
    return Direction((state.direction.value + 1) % len(Direction))

def will_collide(next_position):
    x = next_position.x
    y = next_position.y
    return not (x >= 0 and x < len(EMPTY_GRID[0]) and y >= 0 and y < len(EMPTY_GRID))

def print_usage():
    print('usage: {0} [MODEL]'.format(sys.argv[0]))
    
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
class SimulationContext:
    def __init__(self):
        self.state = None
        self.step_proc = None
        self.draw_proc = None

ROW_COUNT = 10
COL_COUNT = ROW_COUNT
MAX_X = COL_COUNT - 1
MAX_Y = ROW_COUNT - 1

# NOTE(cya): silly python static 2D array syntax
EMPTY_GRID = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
STATIC_GRID = [
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

PIXEL_SCALE = 48
WINDOW_WIDTH = COL_COUNT * PIXEL_SCALE
WINDOW_HEIGHT = ROW_COUNT * PIXEL_SCALE
TARGET_FPS = 10

if __name__ == '__main__':
    main()
