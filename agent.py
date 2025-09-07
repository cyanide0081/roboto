import copy
import heapq
import math
import random
import sys
import time

from collections import deque
from enum import Enum

import pyray as rl

def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    model = sys.argv[1]
    context = crack_context(model)

    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'ロボット')
    rl.set_target_fps(TARGET_FPS)
    rl.set_exit_key(rl.KEY_ENTER)

    while not rl.window_should_close():
        context.step_proc(context.state)
        if not context.state.running:
            break

        rl.begin_drawing()
        context.draw_proc(context.state)
        rl.end_drawing()

    while not rl.window_should_close():
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
        context.state = Mk3State(0)
        context.step_proc = mk3_step_world
        context.draw_proc = mk3_draw_world
    elif model == '3.1':
        context.state = Mk3State(1)
        context.step_proc = mk3_step_world
        context.draw_proc = mk3_draw_world
    elif model == '4':
        context.state = Mk4State()
        context.step_proc = mk4_step_world
        context.draw_proc = mk4_draw_world
    else:
        print_usage()
        sys.exit()

    return context

def mk1_draw_world(state):
    rl.clear_background(rl.BLACK)
    draw_colored_cell(state.position.x, state.position.y, PALETTE['pink'])

def mk1_step_world(state):
    if not state.running:
        state.grid = clone(EMPTY_GRID)
        state.position = pick_random_position(state.grid)
        state.direction = Direction.UP
        state.running = True

    next_position = mk1_move_robot(state)
    while is_out_of_bounds(state.grid, next_position):
        if state.direction == Direction.LEFT:
            state.running = False
            return

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
                draw_colored_cell(x, y, PALETTE['blue'])

def mk2_step_world(state):
    if not state.running:
        state.grid = clone(EMPTY_GRID)
        state.position = pick_random_position(state.grid)
        state.running = True

    next_position = mk2_pick_next_position(state)

    state.grid[state.position.y][state.position.x] = Cell.VISITED
    if next_position == None:
        state.running = False
        return

    state.position = next_position

def mk2_pick_next_position(state):
    direction = mk2_pick_best_direction(state)
    if direction == None:
        return None

    return translate_move(Move(state.position, direction))

def mk2_pick_best_direction(state):
    position = state.position
    steps = {}

    for direction in DIRECTIONS:
        steps[direction] = mk2_get_onward_steps(state, direction)

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

def mk2_1_draw_world(state):
    for y, row in enumerate(state.grid):
        for x, col in enumerate(state.grid[y]):
            if col == Cell.DEBRIS:
                draw_colored_cell(x, y, PALETTE['purple'])

    for y, row in enumerate(state.map):
        for x, col in enumerate(state.map[y]):
            if col <= Cell.FREE.value:
                continue
            elif col == Cell.VISITED.value:
                draw_colored_cell(x, y, PALETTE['blue'])
            elif col == 2:
                draw_colored_cell(x, y, PALETTE['green'])
            elif col == 3:
                draw_colored_cell(x, y, PALETTE['yellow'])
            elif col == 4:
                draw_colored_cell(x, y, PALETTE['orange'])
            else:
                draw_colored_cell(x, y, PALETTE['red'])

def mk2_1_step_world(state):
    if not state.running:
        state.grid = clone(POPULATED_GRID)
        state.map = clone(UNEXPLORED_MAP)
        state.path = deque()
        state.position = pick_random_position(state.grid)
        state.running = True

    state.grid[state.position.y][state.position.x] = Cell.VISITED
    map_cell = get_cell(state.map, state.position)
    if map_cell >= Cell.VISITED.value:
        state.map[state.position.y][state.position.x] += 1
    else:
        state.map[state.position.y][state.position.x] = Cell.VISITED.value

    if grid_is_covered(state.grid):
        state.running = False
        return

    if state.path:
        state.position = state.path.pop()
        return

    position = state.position
    free_neighbors = mk2_1_sense_neighbors(state, position)
    if len(free_neighbors) != 0:
        state.position = mk2_1_pick_best_neighbor(state, free_neighbors)
    else:
        state.path = mk2_1_bfs_to_nearest_frontier(state)
        state.position = state.path.pop()

def mk2_1_sense_neighbors(state, position):
    free_neighbors = {}
    for direction in DIRECTIONS:
        position = translate_move(Move(state.position, direction))
        if is_out_of_bounds(state.grid, position):
            continue

        grid_cell = get_cell(state.grid, position)
        if state.map[position.y][position.x] == Cell.UNEXPLORED.value:
            state.map[position.y][position.x] = grid_cell.value

        map_cell = get_cell(state.map, position)
        if map_cell == Cell.FREE.value:
            free_neighbors[direction] = position

    return free_neighbors

def mk2_1_pick_best_neighbor(state, free_neighbors):
    choices = {}
    for direction, position in free_neighbors.items():
        choices[position] = mk2_get_onward_steps(state, direction)

    return min(choices, key = choices.get)

def mk2_1_bfs_to_nearest_frontier(state):
    goal = get_nearest_frontier(state)

    start = state.position
    parents = make_grid(None)
    visited = make_grid(False)
    visited[start.y][start.x] = True

    q = deque([start])
    while q:
        current = q.popleft()

        if current.equals(goal):
            path = deque()
            while current is not None:
                path.append(current)
                current = parents[current.y][current.x]

            return path

        neighbors = get_adjacent_cells(state.grid, current)
        for neighbor in neighbors:
            cell = get_cell(state.grid, neighbor)
            if cell != Cell.DEBRIS and not get_cell(visited, neighbor):
                visited[neighbor.y][neighbor.x] = True
                parents[neighbor.y][neighbor.x] = current
                q.append(neighbor)

    return None

class Mk2State:
    def __init__(self):
        self.grid = None
        self.map = None
        self.path = None
        self.position = None
        self.direction = None
        self.running = False

def mk3_draw_world(state):
    for y, row in enumerate(state.grid):
        for x, col in enumerate(state.grid[y]):
            if col == Cell.DEBRIS:
                draw_colored_cell(x, y, PALETTE['purple'])
            elif col == Cell.VISITED:
                draw_colored_cell(x, y, PALETTE['yellow'])

    draw_colored_cell(state.start.x, state.start.y, PALETTE['green'])
    draw_colored_cell(state.goal.x, state.goal.y, PALETTE['red'])

def mk3_step_world(state):
    if not state.running:
        if state.kind == 0:
            state.grid = clone(EMPTY_GRID)
        else:
            state.grid = clone(POPULATED_GRID)

        state.start, state.goal = pick_random_points(state.grid)

        state.path = get_astar_path(state)

        state.running = True

    if not state.path:
        state.running = False
    else:
        state.position = state.path.pop()

    state.grid[state.position.y][state.position.x] = Cell.VISITED

class Mk3State:
    def __init__(self, kind):
        self.kind = kind
        self.start = None
        self.goal = None
        self.grid = None
        self.position = None
        self.running = False

def mk4_draw_world(state):
    for y, row in enumerate(state.grid):
        for x, col in enumerate(state.grid[y]):
            if col == 1:
                draw_colored_cell(x, y, PALETTE['green'])
            elif col == 2:
                draw_colored_cell(x, y, PALETTE['yellow'])
            elif col == 3:
                draw_colored_cell(x, y, PALETTE['red'])
            else:
                draw_colored_cell(x, y, PALETTE['purple'])

    draw_colored_cell(state.start.x, state.start.y, PALETTE['blue'])
    draw_colored_cell(state.goal.x, state.goal.y, PALETTE['orange'])


def mk4_step_world(state):
    if not state.running:
        state.grid = clone(WEIGHTED_GRID)
        # state.start, state.goal = pick_random_points(state.grid)
        state.start = Position(5, 0)
        state.goal = Position(5, 9)
        state.path = get_astar_path(state)
        state.running = True

    if not state.path:
        state.running = False
    else:
        state.position = state.path.pop()

    state.grid[state.position.y][state.position.x] = Cell.VISITED

class Mk4State:
    def __init__(self):
        self.start = None
        self.goal = None
        self.grid = None
        self.position = None
        self.running = False

# Generic stuff
def get_cell(grid, position):
    return grid[position.x][position.y]

def pick_random_points(grid):
    start = pick_random_position(grid)
    goal = start

    min_distance = 8
    distance = manhattan_distance(start, goal)
    while goal.equals(start) or distance < min_distance:
        goal = pick_random_position(grid)
        distance = manhattan_distance(start, goal)

    return start, goal

def count_adjacent_visited_cells(grid, position):
    result = 0
    for direction in DIRECTIONS:
        p = translate_move(Move(position, direction))
        if not is_out_of_bounds(grid, p) and get_cell(grid, p) == Cell.VISITED:
            result += 1

    return result

def get_nearest_frontier(state):
    frontiers = {}
    for y, row in enumerate(state.map):
        for x, col in enumerate(state.map[y]):
            if col == Cell.FREE.value:
                position = Position(x, y)
                if position.equals(state.position):
                    continue

                distance = manhattan_distance(state.position, position)
                frontiers[position] = distance

    return min(frontiers, key = frontiers.get)

def manhattan_distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def get_astar_path(state):
    heuristic = manhattan_distance
    start = state.start
    goal = state.goal

    parent_map = make_grid(None)
    closed_map = make_grid(False)

    g_score_map = make_grid(float('inf'))
    g_score_map[state.start.y][state.start.x] = 0

    start_f = heuristic(start, goal)
    open_heap = [(start_f, 0, (start.x, start.y))]
    while open_heap:
        f, g, t = heapq.heappop(open_heap)
        position = Position(t[0], t[1])
        if closed_map[position.y][position.x]:
            continue

        if position.equals(goal):
            path = deque()
            current = position
            while current is not None:
                path.append(current)
                current = parent_map[current.y][current.x]

            return path

        closed_map[position.y][position.x] = True
        for neighbor in get_adjacent_cells(state.grid, position):
            if closed_map[neighbor.y][neighbor.x]:
                continue

            cell_cost = get_cell_cost(state.grid[position.y][position.x])
            if cell_cost == 0:
                continue

            tentative_g = g + cell_cost
            if tentative_g < g_score_map[neighbor.y][neighbor.x]:
                g_score_map[neighbor.y][neighbor.x] = tentative_g
                parent_map[neighbor.y][neighbor.x] = position
                f_score = tentative_g + heuristic(neighbor, goal)
                neighbor_t = (neighbor.x, neighbor.y)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor_t))

    return None

def get_cell_cost(cell):
    if isinstance(cell, Cell):
        return 0 if cell == Cell.DEBRIS else 1
    else:
        return cell

def get_adjacent_cells(grid, position):
    result = []
    for direction in DIRECTIONS:
        current = translate_move(Move(position, direction))
        if not is_out_of_bounds(grid, current):
            result.append(current)

    return result

def draw_colored_cell(x, y, color):
    rl.draw_rectangle(
        x * PIXEL_SCALE,
        y * PIXEL_SCALE,
        PIXEL_SCALE,
        PIXEL_SCALE,
        color
    )

def grid_is_covered(grid):
    for row in grid:
        for col in row:
            if col == Cell.FREE:
                return False

    return True

def pick_random_position(grid):
    unweighted = not isinstance(grid[0][0], Cell)
    while True:
        position = Position(
            random.randint(0, len(grid[0]) - 1),
            random.randint(0, len(grid) - 1)
        )
        if unweighted or grid[position.y][position.x] == Cell.FREE:
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

def get_cell(grid, position):
    return grid[position.y][position.x]

def print_usage():
    print(f'usage: {sys.argv[0]} [MODEL]')

def clone(object):
    return copy.deepcopy(object)

def make_grid(value):
    return [[value for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def equals(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})';

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

DIRECTIONS = [d for d in Direction]

class Cell(Enum):
    DEBRIS = -2
    UNEXPLORED = -1
    FREE = 0
    VISITED = 1

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

D = Cell.DEBRIS
U = Cell.UNEXPLORED
F = Cell.FREE
V = Cell.VISITED

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
WEIGHTED_GRID = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
    [1, 1, 2, 2, 1, 3, 3, 2, 1, 1],
    [1, 1, 2, 1, 3, 3, 3, 2, 1, 1],
    [1, 1, 2, 2, 3, 3, 3, 2, 2, 1],
    [1, 1, 1, 2, 3, 1, 2, 2, 1, 1],
    [1, 1, 1, 1, 2, 3, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

PALETTE = {
    'red': rl.Color(191, 8, 14, 255),
    'green': rl.Color(17, 176, 88, 255),
    'blue': rl.Color(35, 162, 255, 255),
    'yellow': rl.Color(255, 192, 52, 255),
    'orange': rl.Color(240, 106, 70, 255),
    'pink': rl.Color(233, 111, 180, 255),
    'purple': rl.Color(147, 88, 198, 255),
}

UNEXPLORED_MAP = [[U.value for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
EMPTY_MAP = EMPTY_GRID

PIXEL_SCALE = 48
WINDOW_WIDTH = COL_COUNT * PIXEL_SCALE
WINDOW_HEIGHT = ROW_COUNT * PIXEL_SCALE
TARGET_FPS = 15

if __name__ == '__main__':
    main()
