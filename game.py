import curses
import sys
from pprint import pprint

import numpy as np
import pygame
from PIL import Image, ImageDraw


import core
import helpers
from image_viewer import ImageViewer

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"
magic_char = "\033[F"


def delete_last_lines(n=1):
    for _ in range(n):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def step(state):
    state = core.next_state(state)
    return state


class GameState:
    def __init__(self, screen_type="console"):
        self.game = core.Game()
        self.state = core.state
        self.screen_type = screen_type
        self.console = curses.initscr()
        self.score = 0
        self.viewer = None
        self.screen = None
        pygame.init()

    def initial_state(self):
        return (
            helpers.translate_state(self.state, self.game.table),
            0.5,
            False,
        )

    def frame_step(self, action):
        return self.do_action(action)

    def print_console(self, board):
        self.console.addstr(0, 0, board)
        self.console.refresh()

    def render(self, mode="human"):
        if self.viewer is None:
            self.viewer = ImageViewer(caption="SnakeEnv", height=500, width=500,)
        # show the screen on the image viewer
        self.viewer.show(self.screen)

    def find_loc(self, row_ix, col_ix):
        loc = [
            (col_ix * 4.2),
            (row_ix * 4.2),
            (col_ix * 4.2 + 4.2),
            (row_ix * 4.2 + 4.2),
        ]
        return loc

    def draw(self, data):
        img = Image.new("RGB", (128, 128))
        d = ImageDraw.Draw(img)

        for row_ix, row in enumerate(data):
            for col_ix, col in enumerate(row):
                if col == "#":
                    d.rectangle(
                        self.find_loc(row_ix, col_ix), fill=(255, 0, 0),
                    )
                elif col == "X":
                    d.rectangle(
                        self.find_loc(row_ix, col_ix), fill=(0, 255, 0),
                    )
                elif col == "O":
                    d.ellipse(
                        self.find_loc(row_ix, col_ix), fill=(0, 0, 255),
                    )
                elif col == "H":
                    d.rectangle(
                        self.find_loc(row_ix, col_ix), fill=(128, 0, 128),
                    )

        return np.array(img)

    def print_console_data(self, data):
        self.console.addstr(30, 0, data)
        self.console.refresh()

    def do_action(self, action):
        """
        action: In range [0, 1, 2]
                        0 do nothing
                        1 left
                        2 right
                        1, 2 will be translated to respective value according to the snake traveling path.
        """
        self.screen = self.draw(self.game.table)
        new_state, eaten, is_state_terminal = self.driveSnake(action, self.state)
        self.state = new_state

        if eaten:
            reward = 1
            self.score += 1
        elif is_state_terminal and not eaten:
            reward = -1
            self.score = 0
        else:
            reward = -0.05
        return (
            helpers.translate_state(new_state, self.game.table),
            reward,
            is_state_terminal,
            self.score,
        )

    def driveSnake(self, direction, state):
        traveling_path = state["moves"][0]

        if traveling_path == core.NORTH:
            move = core.WEST if direction == 1 else core.EAST
        elif traveling_path == core.SOUTH:
            move = core.EAST if direction == 1 else core.WEST

        elif traveling_path == core.WEST:
            move = core.SOUTH if direction == 1 else core.NORTH
        elif traveling_path == core.EAST:
            move = core.NORTH if direction == 1 else core.SOUTH
        else:
            raise ValueError("Invalid travelling path.")

        if direction == 0:
            move = self.state["moves"][0]

        new_state = core.enqeue_move(state, move)

        new_state, eaten, is_state_terminal = core.next_state(new_state)

        self.game.make(new_state, new_state["apple"])

        if self.screen_type == "console":
            board = str(self.game)
            self.print_console(board)
        else:
            self.render()  # use a gui

        return new_state, eaten, is_state_terminal
