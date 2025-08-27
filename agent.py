from enum import Enum
import sys
import time
import random
import pyray as rl

TARGET_FPS = 10
ROW_COUNT = 10
COL_COUNT = ROW_COUNT

# NOTE(cya): silly python static array syntax
GRID = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
PIXELS_PER_SLOT = 48

WINDOW_WIDTH = COL_COUNT * PIXELS_PER_SLOT
WINDOW_HEIGHT = ROW_COUNT * PIXELS_PER_SLOT

MAX_X = COL_COUNT - 1
MAX_Y = ROW_COUNT - 1

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    context = SimulationContext(None, None)
    model = sys.argv[1]
    if model == '1':
        context.state = Mk1State()
        context.draw_proc = mk1_draw_world
        context.step_proc = mk1_step_world
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
        
def pick_initial_direction(state):
    distance_top = state.position.y
    distance_right = MAX_X - state.position.x
    distance_bottom = MAX_Y - state.position.y
    distance_left = state.position.x

    min_distance = min([
        distance_top,
        distance_right,
        distance_bottom,
        distance_left,
    ])
    if min_distance == distance_top:
        state.direction = Direction.UP
    elif min_distance == distance_right:
        state.direction = Direction.RIGHT
    elif min_distance == distance_bottom:
        state.direction = Direction.DOWN
    else:
        state.direction = Direction.LEFT

    if will_collide(state.position):
        state.direction = rotate_robot_clockwise(state)
    
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

def mk1_draw_world(state):
    rl.clear_background(rl.BLACK)
    rl.draw_rectangle(
        state.position.x * PIXELS_PER_SLOT,
        state.position.y * PIXELS_PER_SLOT,
        PIXELS_PER_SLOT,
        PIXELS_PER_SLOT,
        rl.PINK
    )

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
    def __init__(self, draw_proc, update_proc):
        self.draw_proc = draw_proc
        self.update_proc = update_proc

def print_usage():
    print('usage: {0} [MODEL]'.format(sys.argv[0]))
    
if __name__ == '__main__':
    main()
