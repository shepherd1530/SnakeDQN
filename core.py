import random

import helpers

from pprint import pprint

NORTH = {"x": 0, "y": -1}
WEST = {"x": -1, "y": 0}
SOUTH = {"x": 0, "y": 1}
EAST = {"x": 1, "y": 0}


WIDTH, HEIGHT = 30, 30


def make_apple(row, col, snake):
    def rand():
        x = random.randrange(0, col - 1)
        y = random.randrange(0, row - 1)

        while y == 0 or y == HEIGHT - 1:
            y = random.randrange(0, row - 1)

        while x == 0 or x == WIDTH - 1:
            x = random.randrange(0, col - 1)

        loc = {"x": x, "y": y}
        return loc

    loc = rand()

    while loc in snake:  # Needs optimization
        loc = rand()

    return loc


state = {
    "snake": [],
    "cols": WIDTH,
    "rows": HEIGHT,
    "moves": [EAST],
    "apple": make_apple(row=HEIGHT, col=WIDTH, snake=[]),
}


def next_head(state):
    if not len(state["snake"]) == 0:  # shot circuit for the most popular condition
        new_head = {}
        new_head["x"] = helpers.mod(
            state["cols"], (state["snake"][0]["x"] + state["moves"][0]["x"])
        )
        new_head["y"] = helpers.mod(
            state["rows"], (state["snake"][0]["y"] + state["moves"][0]["y"])
        )
        return new_head
    else:
        return {"x": 1, "y": 1}


def are_points_equal(snake_head, apple):
    return snake_head["x"] == apple["x"] and snake_head["y"] == apple["y"]


def will_eat(state):
    return are_points_equal(next_head(state), state["apple"])


def will_crash(state):
    next_head_ = next_head(state)
    self_crash = any([are_points_equal(next_head_, path) for path in state["snake"]])
    wall_crash = (next_head_["y"] == 0 or next_head_["y"] == HEIGHT - 1) or (
        next_head_["x"] == 0 or next_head_["x"] == WIDTH - 1
    )

    return self_crash or wall_crash


def is_valid_move(state, move):
    invalid_x_axis = move["x"] + state["moves"][0]["x"] != 0
    invalid_y_axis = move["y"] + state["moves"][0]["y"] != 0
    return invalid_y_axis and invalid_x_axis


def next_moves(state):
    if len(state["moves"]) > 1:
        return helpers.drop_first(state["moves"])
    else:
        return state["moves"]


def next_apple(state):
    if will_eat(state):
        return make_apple(row=HEIGHT, col=WIDTH, snake=state["snake"])  # make_apple()
    else:
        if not will_crash(state):
            return state["apple"]
        else:
            return make_apple(row=HEIGHT, col=WIDTH, snake=state["snake"])


def next_snake(state):
    eaten = False
    if not will_crash(state):
        if not will_eat(state):
            new_snake = [next_head(state)]
            new_snake.extend(helpers.drop_last(state["snake"]))
            return new_snake, eaten
        else:
            eaten = True
            new_snake = [next_head(state)]
            new_snake.extend(state["snake"])
            return new_snake, eaten
    else:
        return [], eaten


def next_state(state):
    new_state = {}
    new_state["rows"] = state["rows"]
    new_state["cols"] = state["cols"]

    new_state["moves"] = next_moves(state)

    new_snake_, eaten = next_snake(state)
    new_state["snake"] = new_snake_

    new_state["apple"] = next_apple(state)
    is_state_terminal = False

    if not new_state["snake"]:
        new_state["moves"] = [EAST]
        is_state_terminal = True
    elif eaten:
        is_state_terminal = True

    return new_state, eaten, is_state_terminal


def enqeue_move(state, move):
    if is_valid_move(state, move):
        old_state_moves = state["moves"]
        old_state_moves.extend([move])
        new_state = helpers.merge(state, {"moves": old_state_moves})
        return new_state
    else:
        return state


class Game:
    def __init__(self, row=HEIGHT, col=WIDTH):
        self.table = self.init_table(row, col, game_type="classc")
        self.addSnake()
        self.addApple()

    def __str__(self):
        val = "\n".join(list(map(lambda xs: " ".join(xs), self.table)))
        return val

    def addSnake(self, state=state):
        for ix, _ in enumerate(state["snake"]):
            val = "X" if ix != 0 else "H"
            self.table[state["snake"][ix]["y"]][state["snake"][ix]["x"]] = val

    def addApple(self, apple=state["apple"]):
        self.table[apple["y"]][apple["x"]] = "O"

    def make(self, state, apple, row=HEIGHT, col=WIDTH):
        self.table = self.init_table(row, col, game_type="clssic")
        self.addSnake(state)
        self.addApple(apple)
        self.addCrash(state)

    def addCrash(self, state, row=HEIGHT, col=WIDTH):
        if len(state["snake"]) == 0:
            self.table = [["#" for x in range(col)] for ix in range(row)]

    def init_table(self, row, col, game_type="classic"):
        if game_type == "classic":
            return [["." for x in range(col)] for ix in range(row)]
        else:
            table = []

            for ix in range(row):
                temp = []
                for x in range(col):
                    val = (
                        "#"
                        if (x == 0 or x == col - 1) or (ix == 0 or ix == row - 1)
                        else "."
                    )
                    temp.append(val)
                table.append(temp)

            return table
