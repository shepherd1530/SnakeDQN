import curses
import random
from random import sample

# import keyboard
import pygame
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

import game

from DQN import DeepSnakeNetwork

import signal
import sys


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
    out = F.softmax(out * 50, dim=0).multinomial(1)
    out = out.data[0]
    print(out)
    return out


def do_checkpoint(model, epoch, optimizer, loss, loss_history, score):
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "loss": loss,
            "loss_history": loss_history,
        },
        f"./checkpoint_at_epoch_{epoch}_with_score_{score}.tar",
    )


agent = DeepSnakeNetwork(16, 3)

print(count_parameters(agent))

optimizer = optim.SGD(agent.parameters(), lr=5e-2)

criterion = F.smooth_l1_loss
epsilon = agent.initial_epsilon
decay = 0.999996

replay_memory = []
game_state = game.GameState()
state = torch.tensor(game_state.initial_state()[0], dtype=torch.float32)


losses = []
loss_counter = 0
epoch_loss = 0

max_score, old_score = 0, 0


for epoch in range(agent.number_of_iterations):
    output = agent(state)  # [0]

    perform_random_action = random.random() <= epsilon
    action = (
        torch.tensor(random.randrange(0, 3))
        if perform_random_action
        else select_action(output)
    )

    new_state, new_reward, is_state_terminal, score = game_state.frame_step(action)

    if score > max_score:
        old_score = max_score
        max_score = score
        # do_checkpoint(agent, epoch, optimizer, epoch_loss, losses, max_score)

    replay_memory.append(
        (
            state.unsqueeze(0),
            action.unsqueeze(0),
            torch.tensor(new_reward, dtype=torch.float32).unsqueeze(0),
            torch.tensor(new_state, dtype=torch.float32).unsqueeze(0),
            is_state_terminal,
        )
    )

    if len(replay_memory) > agent.replay_memory_size:
        replay_memory.pop(0)

    epsilon = max(agent.final_epsilon, epsilon * decay)

    samples = list(
        zip(
            *random.sample(replay_memory, min(len(replay_memory), agent.minibatch_size))
        )
    )
    state_batch, action_batch, reward_batch, new_state_batch = list(
        map(lambda x: torch.cat(x, 0), samples[:-1])
    )
    terminal_batch = samples[-1]

    new_output_batch = agent(new_state_batch)

    y_batch = torch.tensor(
        tuple(
            reward_batch[i].detach()
            if terminal_batch[i]
            else reward_batch[i].detach() + agent.gamma * torch.max(new_output_batch[i])
            for i in range(min(len(replay_memory), agent.minibatch_size))
        )
    )

    batch_out = agent(state_batch)

    q_value = batch_out.gather(1, action_batch.unsqueeze(1))

    optimizer.zero_grad()

    loss = criterion(q_value, y_batch.unsqueeze(1))
    loss_item = loss.item()
    loss_counter += 1
    losses.append(loss_item / agent.minibatch_size)
    epoch_loss += loss_item / agent.minibatch_size

    if loss_counter % 250 == 0:
        game_state.print_console_data(
            f"epoch_loss: {epoch_loss}, epsilon: {epsilon}, epoch: {epoch}, max_score: {max_score}"
        )

    # if epoch % 25000 == 0:
    # do_checkpoint(agent, epoch, optimizer, epoch_loss, losses, max_score)

    loss.backward()
    optimizer.step()

    state = torch.tensor(new_state, dtype=torch.float32)
