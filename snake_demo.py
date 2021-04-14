import curses
import signal
import sys

import keyboard
import pygame
import torch
import torch.nn.functional as F
import torch.optim as optim
from matplotlib import pyplot as plt

from DQN import DeepSnakeNetwork
from game import GameState


def signal_handler(signal, frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

clock = pygame.time.Clock()


def check_exit():
    if keyboard.is_pressed("ctrl + c"):
        curses.endwin()
        pygame.quit()


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def select_action(out):
    out = F.softmax(out * 250, dim=0).multinomial(1)
    out = out.data[0]
    return out


checkpoint = torch.load("checkpoint_max.tar")

agent = DeepSnakeNetwork(16, 3)
agent.load_state_dict(checkpoint["model_state_dict"])

agent.eval()

optimizer = optim.SGD(agent.parameters(), lr=1e-2)
criterion = F.smooth_l1_loss
epsilon = agent.initial_epsilon
decay = 0.999996

replay_memory = []
game_state = GameState()
state = torch.tensor(game_state.initial_state()[0], dtype=torch.float32)

losses = []
loss_counter = 0
epoch_loss = 0

max_score, old_score = 0, 0

for epoch in range(agent.number_of_iterations):
    check_exit()
    clock.tick(10)
    output = agent(state)

    action = select_action(output)

    new_state, new_reward, is_state_terminal, score = game_state.frame_step(action)

    if score > max_score:
        old_score = max_score
        max_score = score

    game_state.print_console_data(f"current score: {score}, max score: {max_score}")
    state = torch.tensor(new_state, dtype=torch.float32)
