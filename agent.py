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
        state.grid = EMTPY_GRID.copy()
        state.position = pick_random_position(state.grid)
        state.direction = Direction.UP
        state.running = True
    
    next_position = mk1_move_robot(state)
    while is_illegal_position(state.grid, next_position):
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
        self.grid = None
        self.position = None
        self.direction = None
        self.running = False

def mk2_draw_world(state):
    for y, row in enumerate(state.grid):
        for x, col in enumerate(state.grid[y]):
            if col == Cell.VISITED:
                draw_colored_cell(x, y, rl.BLUE)
            elif col == Cell.DEBRIS:
                draw_colored_cell(x, y, rl.PURPLE)
    
def mk2_step_world(state):
    if not state.running:
        state.grid = POPULATED_GRID.copy()
        state.position = pick_random_position(state.grid)
        state.running = True

    next_position = mk2_pick_next_position(state)
    if next_position == None:
        state.running = False
        return

    state.grid[state.position.x][state.position.y] = Cell.VISITED
    state.position = next_position
    
def mk2_pick_next_position(state):
    direction = mk2_pick_best_direction(state)
    if direction == None:
        return None

    return translate_move(Move(state.position, direction))

def mk2_pick_best_direction(state):
    position = state.position
    steps = {}
    
    steps[Direction.UP] = mk2_get_onward_steps(state, Direction.UP)
    steps[Direction.RIGHT] = mk2_get_onward_steps(state, Direction.RIGHT)
    steps[Direction.DOWN] = mk2_get_onward_steps(state, Direction.DOWN)
    steps[Direction.LEFT] = mk2_get_onward_steps(state, Direction.LEFT)

    steps = dict(filter(lambda x: x[1] > 0, steps.items()))
    if len(steps) == 0:
        return None

    choice = min(steps.items(), key = lambda x: x[1])
    return choice[0]

def mk2_get_onward_steps(state, direction):
    position = state.position
    steps = 0
    while True:
        position = translate_move(Move(position, direction))
        if is_illegal_position(state.grid, position):
            break

        steps += 1

    return steps

class Mk2State:
    def __init__(self):
        self.position = None
        self.direction = None
        self.running = False
        
# Generic stuff        
def draw_colored_cell(x, y, color):
    rl.draw_rectangle(
        x * PIXEL_SCALE,
        y * PIXEL_SCALE,
        PIXEL_SCALE,
        PIXEL_SCALE,
        color
    )
    
def pick_random_position(grid):
    return Position(
        random.randint(0, len(grid[0]) - 1),
        random.randint(0, len(grid) - 1)
    )

def translate_move(move):
    x = move.position.x
    y = move.position.y
    direction = move.direction
    if direction == Direction.UP:
        return Position(x, y - 1)
    elif direction == Direction.RIGHT:
        return Position(x + 1, y)
    elif direction == Direction.DOWN:
        return Position(x, y + 1)
    elif direction == Direction.LEFT:
        return Position(x - 1, y)
    
def rotate_robot_clockwise(state):
    return Direction((state.direction.value + 1) % len(Direction))

def is_illegal_position(grid, position):
    x = position.x
    y = position.y
    in_bounds = (x >= 0 and x < len(grid[0]) and y >= 0 and y < len(grid))
    return not in_bounds or grid[x][y] == Cell.DEBRIS

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

class Cell(Enum):
    FREE = 0
    VISITED = 1
    DEBRIS = 2
    
class Move:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction

class SimulationContext:
    def __init__(self):
        self.state = None
        self.step_proc = None
        self.draw_proc = None

ROW_COUNT = 10
COL_COUNT = ROW_COUNT

F = Cell.FREE
D = Cell.DEBRIS

EMPTY_GRID = [[F for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
POPULATED_GRID = [
    [F, F, F, F, D, F, F, F, F, F],
    [D, F, F, D, F, F, F, F, F, F],
    [F, F, D, F, F, F, F, F, F, F],
    [F, F, D, F, F, D, F, F, F, F],
    [F, D, F, F, F, F, D, F, F, F],
    [F, F, F, D, F, D, D, D, D, F],
    [F, F, F, F, F, D, F, F, D, F],
    [F, F, F, F, F, D, F, F, D, F],
    [F, F, F, F, F, D, F, D, D, F],
    [F, F, F, F, F, D, F, F, F, F],
]

PIXEL_SCALE = 48
WINDOW_WIDTH = COL_COUNT * PIXEL_SCALE
WINDOW_HEIGHT = ROW_COUNT * PIXEL_SCALE
TARGET_FPS = 10

if __name__ == '__main__':
    main()
