import torch.nn as nn


class DeepSnakeNetwork(nn.Module):
    def __init__(self, state_size, out_size):
        super(DeepSnakeNetwork, self).__init__()

        self.state_size = state_size
        self.out_size = out_size
        self.gamma = 0.99
        self.final_epsilon = 0.0001
        self.initial_epsilon = 0.9
        self.number_of_iterations = 100000000
        self.replay_memory_size = 10000000
        self.minibatch_size = 2048

        self.fc1 = nn.Linear(state_size, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, out_size)
        self.relu1 = nn.ReLU(inplace=True)
        self.relu2 = nn.ReLU(inplace=True)

    def forward(self, batch):
        out = self.fc1(batch)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        return out
