
import os
import torch
import numpy as np
from key_management.autoencoder_keygen import AutoencoderKeygen
from key_management.dql_rotation_agent import RotationAgent

class IntegrationController:
    def __init__(self, project_root, device='cpu'):
        self.project_root = project_root
        self.device = device

        self.ckpt_autoenc = os.path.join(project_root, 'key_management', 'autoencoder_ckpt.pth')
        self.ckpt_agent = os.path.join(project_root, 'key_management', 'dql_rotation_agent_ckpt.pth')

        # Initialize keygen
        self.keygen = AutoencoderKeygen(self.ckpt_autoenc, device=device)
        if os.path.exists(self.ckpt_autoenc):
            self.keygen.load_model(self.ckpt_autoenc)

        # Initialize agent
        self.agent = RotationAgent(device=device)
        if os.path.exists(self.ckpt_agent):
            self.agent.load(self.ckpt_agent, map_location=device)
            print('✅ Models loaded successfully')

        # Track the current key and usage stats
        self.current_key = None
        self.usage_count = 0
        self.risk_score = 0.1

    def generate_key(self):
        #Generate a fresh cryptographic key
        key = self.keygen.generate_key()
        self.current_key = key
        self.usage_count = 0
        print('🔐 Generated new key.')
        return key

    def simulate_usage(self, steps=10):
        #Simulate encrypt/decrypt operations and possible rotations
        if self.current_key is None:
            self.generate_key()

        for step in range(steps):
            # Simulate increase in risk and usage
            self.usage_count += 1
            self.risk_score = min(1.0, self.risk_score + np.random.uniform(0.05, 0.15))

            # State: [usage_count_norm, risk_score, random_noise, bias]
            state = np.array([
                self.usage_count / 50.0,
                self.risk_score,
                np.random.rand(),
                1.0
            ], dtype=np.float32)

            # Decide whether to rotate
            action = self.agent.select_action(state, epsilon=0.0)
            if action == 1:  # 1 = rotate
                print(f"🔁 Step {step}: rotating key (usage={self.usage_count}, risk={self.risk_score:.2f})")
                self.generate_key()
                self.risk_score = 0.1
            else:
                print(f"➡️  Step {step}: continue with current key (usage={self.usage_count}, risk={self.risk_score:.2f})")

        print('\n✅ Simulation complete.')
