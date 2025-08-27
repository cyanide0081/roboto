from enum import Enum
import sys
import time
import random
import pyray as rl

ROW_COUNT = 10
COL_COUNT = ROW_COUNT
MAX_X = COL_COUNT - 1
MAX_Y = ROW_COUNT - 1

# NOTE(cya): silly python static 2D array syntax
GRID = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]

PIXEL_SCALE = 48
WINDOW_WIDTH = COL_COUNT * PIXEL_SCALE
WINDOW_HEIGHT = ROW_COUNT * PIXEL_SCALE
TARGET_FPS = 10

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
        print('not implemented')
        return
    elif model == '3':
        print('not implemented')
        return
    elif model == '4':
        print('not implemented')
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
    
def mk1_draw_world(state):
    rl.clear_background(rl.BLACK)
    rl.draw_rectangle(
        state.position.x * PIXEL_SCALE,
        state.position.y * PIXEL_SCALE,
        PIXEL_SCALE,
        PIXEL_SCALE,
        rl.PINK
    )
    
def mk1_step_world(state):
    if state.position == None:
        state.position = Position(
            random.randint(0, MAX_X),
            random.randint(0, MAX_Y)
        )
        state.direction = Direction.UP
    
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

def rotate_robot_clockwise(state):
    return Direction((state.direction.value + 1) % len(Direction))

def will_collide(next_position):
    x = next_position.x
    y = next_position.y
    return not (x >= 0 and x < len(GRID[0]) and y >= 0 and y < len(GRID))

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
class Mk1State:
    def __init__(self):
        self.position = None
        self.direction = None
        self.running = True

class SimulationContext:
    def __init__(self):
        self.state = None
        self.step_proc = None
        self.draw_proc = None

def print_usage():
    print('usage: {0} [MODEL]'.format(sys.argv[0]))
    
if __name__ == '__main__':
    main()
