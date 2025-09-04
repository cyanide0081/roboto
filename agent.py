from enum import Enum
import sys
import time
import random
import pyray as rl

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    model = sys.argv[1]
    context = crack_context(model)
    
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
    
def crack_context(model):
    context = SimulationContext()
    if model == '1':
        context.state = Mk1State()
        context.step_proc = mk1_step_world
        context.draw_proc = mk1_draw_world
    elif model == '2':
        context.state = Mk2State()
        context.step_proc = mk2_step_world
        context.draw_proc = mk2_draw_world
    elif model == '2.1':
        context.state = Mk2State()
        context.step_proc = mk2_1_step_world
        context.draw_proc = mk2_1_draw_world
    elif model == '3':
        context.state = Mk3State()
        context.step_proc = mk3_step_world
        context.draw_proc = mk3_draw_world
    elif model == '3.1':
        context.state = Mk3State()
        context.step_proc = mk3_1_step_world
        context.draw_proc = mk3_1_draw_world
    elif model == '4':
        context.state = Mk4State()
        context.step_proc = mk4_step_world
        context.draw_proc = mk4_draw_world
    else:
        print_usage()
        sys.exit()

    return context

# Mk1 model
def mk1_draw_world(state):
    rl.clear_background(rl.BLACK)
    draw_colored_cell(state.position.x, state.position.y, rl.PINK)
    
def mk1_step_world(state):
    if not state.running:
        state.grid = EMPTY_GRID.copy()
        state.position = pick_random_position(state.grid)
        state.direction = Direction.UP
        state.running = True
    
    next_position = mk1_move_robot(state)
    while is_out_of_bounds(state.grid, next_position):
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
    
def mk2_step_world(state):
    if not state.running:
        state.grid = EMPTY_GRID.copy()
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
    ties = dict(filter(lambda x: x[1] == choice[1], steps.items()))
    if len(ties) > 1:
        mk2_break_ties(ties, state.grid, position)
        choice = min(steps.items(), key = lambda x: x[1])

    return choice[0]

def mk2_get_onward_steps(state, direction):
    grid = state.grid
    position = state.position
    steps = 0
    while True:
        position = translate_move(Move(position, direction))
        if is_out_of_bounds(grid, position):
            break

        cell = get_cell(grid, position)
        if cell == Cell.DEBRIS or cell == Cell.VISITED:
            break

        steps += 1 

    return steps

def mk2_break_ties(ties, grid, position):
    for tie in ties.items():
        pos = translate_move(Move(position, tie[0]))
        count = count_adjacent_visited_cells(grid, pos)
        ties[tie[0]] -= count

def get_cell(grid, position):
    return grid[position.x][position.y]

def count_adjacent_visited_cells(grid, position):
    result = 0
    up = translate_move(Move(position, Direction.UP))
    if not is_out_of_bounds(grid, up) and get_cell(grid, up) == Cell.VISITED: 
        result += 1
    right = translate_move(Move(position, Direction.RIGHT))
    if not is_out_of_bounds(grid, right) and get_cell(grid, right) == Cell.VISITED: 
        result += 1
    down = translate_move(Move(position, Direction.DOWN))
    if not is_out_of_bounds(grid, down) and get_cell(grid, down) == Cell.VISITED: 
        result += 1
    left = translate_move(Move(position, Direction.LEFT))
    if not is_out_of_bounds(grid, left) and get_cell(grid, left) == Cell.VISITED: 
        result += 1

    return result

def mk2_1_draw_world(state):
    for y, row in enumerate(state.grid):
        for x, col in enumerate(state.grid[y]):
            if col == Cell.VISITED:
                draw_colored_cell(x, y, rl.BLUE)
            elif col == Cell.DEBRIS:
                draw_colored_cell(x, y, rl.PURPLE)
    
def mk2_1_step_world(state):
    if not state.running:
        state.grid = POPULATED_GRID.copy()
        state.position = pick_random_position(state.grid)
        state.running = True

    # next_position = mk2_pick_next_position(state)
    # if next_position == None:
    #     state.running = False
    #     return

    # state.grid[state.position.x][state.position.y] = Cell.VISITED
    # state.position = next_position

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
    while True:
        position = Position(
            random.randint(0, len(grid[0]) - 1),
            random.randint(0, len(grid) - 1)
        )
        if grid[position.x][position.y] != Cell.DEBRIS:
            return position

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

def is_out_of_bounds(grid, position):
    x = position.x
    y = position.y
    return not (x >= 0 and x < len(grid[0]) and y >= 0 and y < len(grid))

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
TARGET_FPS = 15

if __name__ == '__main__':
    main()
