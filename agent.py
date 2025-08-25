from enum import Enum
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
    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'ロボット')
    rl.set_target_fps(TARGET_FPS)
    
    state = State(Position(
        random.randint(0, MAX_X),
        random.randint(0, MAX_Y)
    ))
    pick_initial_direction(state)
    while state.running and not rl.window_should_close():
        # TODO(cya): abstract the simulation running part based on argv[1] to
        # select the agent model (from 1 to 4)
        
        rl.begin_drawing()
        draw_world(state)
        rl.end_drawing()
        
        update_world(state)
        
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
        state.walls_reached.append(state.direction) 
        state.direction = rotate_robot_clockwise(state)
    
def update_world(state):
    next_position = move_robot(state)
    if will_collide(next_position):
        state.walls_reached.append(state.direction) 
        state.direction = rotate_robot_clockwise(state)
        next_position = move_robot(state)
    
    if len(state.walls_reached) == len(Direction):
        state.running = False
        
    state.position = next_position

def move_robot(state):
    next_position = Position(state.position.x, state.position.y)
    if state.direction == Direction.UP:
        next_position.y -= 1
    elif state.direction == Direction.RIGHT:
        next_position.x += 1
    elif state.direction == Direction.DOWN:
        next_position.y += 1
    else:
        next_position.x -= 1

    return next_position

def rotate_robot_clockwise(state):
    return Direction((state.direction.value + 1) % len(Direction))

def will_collide(next_position):
    x = next_position.x
    y = next_position.y
    return not (x >= 0 and x < len(GRID[0]) and y >= 0 and y < len(GRID))

def draw_world(state):
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
    
class State:
    def __init__(self, position):
        self.position = position
        self.direction = None
        self.walls_reached = []
        self.running = True

if __name__ == '__main__':
    main()
