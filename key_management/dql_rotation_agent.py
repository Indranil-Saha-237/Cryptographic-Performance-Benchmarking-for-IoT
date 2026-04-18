
import numpy as np
import random
import os
import torch
import torch.nn as nn
import torch.optim as optim

class SimpleDQN(nn.Module):
    def __init__(self, state_dim=4, action_dim=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.net(x)

class RotationAgent:
    def __init__(self, state_dim=4, action_dim=3, device='cpu'):
        self.device = device
        self.net = SimpleDQN(state_dim, action_dim).to(device)
        self.target = SimpleDQN(state_dim, action_dim).to(device)
        self.target.load_state_dict(self.net.state_dict())
        self.optimizer = optim.Adam(self.net.parameters(), lr=1e-3)
        self.criterion = nn.MSELoss()
        self.gamma = 0.99
        self.action_dim = action_dim

    def select_action(self, state, epsilon=0.1):
        if random.random() < epsilon:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            s = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            q = self.net(s)
            return int(q.argmax().item())

    def train_step(self, batch):
        s = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=self.device)
        a = torch.tensor([b[1] for b in batch], dtype=torch.long, device=self.device).unsqueeze(1)
        r = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=self.device).unsqueeze(1)
        s2 = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=self.device)
        done = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=self.device).unsqueeze(1)

        q_values = self.net(s).gather(1, a)
        with torch.no_grad():
            q_next = self.target(s2).max(1)[0].unsqueeze(1)
            q_target = r + (1 - done) * self.gamma * q_next

        loss = self.criterion(q_values, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def update_target(self):
        self.target.load_state_dict(self.net.state_dict())

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({'net': self.net.state_dict(), 'target': self.target.state_dict()}, path)

    def load(self, path, map_location='cpu'):
        ckpt = torch.load(path, map_location=map_location)
        self.net.load_state_dict(ckpt['net'])
        self.target.load_state_dict(ckpt['target'])
