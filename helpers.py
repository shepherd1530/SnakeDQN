import random
import core


def drop_first(moves):
    return moves[1:]


def drop_last(moves):
    return moves[:-1]


def random_pos(state):
    data = {}
    data["x"] = random.randrange(0, state["cols"] - 1)
    data["y"] = random.randrange(0, state["rows"] - 1)
    return data


def merge(state, moves):
    return {**state, **moves}


def mod(x, y):
    return ((y % x) + x) % x


def get_apple_coordinates(state):
    apple_target = [0] * 4

    try:
        x_diff = state["snake"][0]["x"] - state["apple"]["x"]
        y_diff = state["snake"][0]["y"] - state["apple"]["y"]
    except IndexError:  # No apple, snake just crashed.
        x_diff = 1 - state["apple"]["x"]
        y_diff = 1 - state["apple"]["y"]

    if x_diff > 0:
        apple_target[3] = 1  # WEST
    elif x_diff < 0:
        apple_target[1] = 1  # EAST

    if y_diff > 0:
        apple_target[0] = 1  # NORTH
    elif y_diff < 0:
        apple_target[2] = 1  # SOUTH

    return apple_target


def get_head_traveling_path(state):
    head_target = [0] * 4

    if state["moves"][0] == core.NORTH:
        head_target[0] = 1
    elif state["moves"][0] == core.WEST:
        head_target[3] = 1
    elif state["moves"][0] == core.SOUTH:
        head_target[2] = 1
    elif state["moves"][0] == core.EAST:
        head_target[1] = 1
    else:
        raise Exception("Invalid direction")

    return head_target


def get_surrounding_pos(state, board):
    def compare(y, x):
        return board[y][x] != "." or board[y][x] != "O"

    values = [0] * 8

    if not state["snake"]:
        new = [1, 1, 0, 0, 0, 1, 1, 1]
        return new

    head_x, head_y = (
        state["snake"][0]["x"],
        state["snake"][0]["y"],
    )  # dicts are unordered cant unpack

    if compare(head_y - 1, head_x):
        values[0] = 1
    if compare(head_y - 1, head_x + 1):
        values[1] = 1

    if compare(head_y, head_x + 1):
        values[2] = 1
    if compare(head_y + 1, head_x + 1):
        values[3] = 1

    if compare(head_y + 1, head_x):
        values[4] = 1
    if compare(head_y + 1, head_x - 1):
        values[5] = 1

    if compare(head_y, head_x - 1):
        values[6] = 1
    if compare(head_y - 1, head_x - 1):
        values[7] = 1

    return values


def translate_state(state, board):
    apple_target = get_apple_coordinates(state)
    head_target = get_head_traveling_path(state)
    immediate_danger = get_surrounding_pos(state, board)
    out = [*immediate_danger, *head_target, *apple_target]
    return out
