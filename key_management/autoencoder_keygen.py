# autoencoder_keygen.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

# -------------------------------
# MNIST Autoencoder Definition (784 input for 28x28 images)
# -------------------------------
class SimpleAutoencoder(nn.Module):
  def __init__(self, input_dim=784, latent_dim=32):
    super(SimpleAutoencoder, self).__init__()
    self.encoder = nn.Sequential(
      nn.Linear(input_dim, 256),
      nn.ReLU(),
      nn.Linear(256, 128),
      nn.ReLU(),
      nn.Linear(128, latent_dim)
    )
    self.decoder = nn.Sequential(
      nn.Linear(latent_dim, 128),
      nn.ReLU(),
      nn.Linear(128, 256),
      nn.ReLU(),
      nn.Linear(256, input_dim),
      nn.Sigmoid()
    )

  def forward(self, x):
    z = self.encoder(x)
    out = self.decoder(z)
    return out

# -------------------------------
# AutoencoderKeygen Class
# -------------------------------
class AutoencoderKeygen:
  def __init__(self, save_path, input_dim=784, latent_dim=32, device="cpu"):
    self.save_path = save_path
    self.input_dim = input_dim
    self.latent_dim = latent_dim
    self.device = device
    self.model = SimpleAutoencoder(input_dim, latent_dim).to(device)

  def train_autoencoder(self, train_loader=None, epochs=30):
    opt = optim.Adam(self.model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    # Use provided data loader or generate random data
    if train_loader is None:
      data = torch.rand(500, self.input_dim).to(self.device)
      use_dataloader = False
    else:
      use_dataloader = True

    self.model.train()
    for epoch in range(epochs):
      total_loss = 0
      batch_count = 0

      if use_dataloader:
        # Train on MNIST data
        for batch_idx, (data, _) in enumerate(train_loader):
          data = data.to(self.device)

          reconstructed = self.model(data)
          loss = criterion(reconstructed, data)

          opt.zero_grad()
          loss.backward()
          opt.step()

          total_loss += loss.item()
          batch_count += 1

          if batch_idx >= 100:  # Limit batches per epoch for speed
            break

        avg_loss = total_loss / batch_count
        print(f"Epoch {epoch} avg loss {avg_loss:.6f}")
      else:
        # Train on random data (original behavior)
        idx = torch.randperm(data.size(0))[:64]
        batch = data[idx]

        reconstructed = self.model(batch)
        loss = criterion(reconstructed, batch)

        opt.zero_grad()
        loss.backward()
        opt.step()

        print(f"Epoch {epoch} loss {loss.item():.6f}")

    # Save model
    os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
    torch.save(self.model.state_dict(), self.save_path)
    print(f"✅ Autoencoder saved to {self.save_path}")

  def load_model(self, path):
    self.model.load_state_dict(torch.load(path, map_location=self.device))
    self.model.eval()
    print(f"✅ Model loaded from {path}")

  def generate_key(self, seed=None):
    if seed is not None:
      torch.manual_seed(seed)
      np.random.seed(seed)

    self.model.eval()
    with torch.no_grad():
      random_input = torch.rand(1, self.input_dim).to(self.device)
      latent = self.model.encoder(random_input)
      key_vector = latent.squeeze().cpu().numpy()

      # Convert to hex
      key_bytes = (np.abs(key_vector) * 255).astype(np.uint8).tobytes()
      key_hex = key_bytes.hex()
      return key_hex

# -------------------------------
# Standalone functions for backward compatibility
# -------------------------------
def train_autoencoder(save_path, train_loader=None, epochs=30, device='cpu'):
  keygen = AutoencoderKeygen(save_path, device=device)
  keygen.train_autoencoder(train_loader=train_loader, epochs=epochs)
  return keygen.model

def generate_key(model_path, seed=None, device='cpu'):
  keygen = AutoencoderKeygen(model_path, device=device)
  keygen.load_model(model_path)
  return keygen.generate_key(seed=seed)

def generate_key_from_seed(model_path, seed_array, device='cpu'):
  # For compatibility with numpy array seeds
  seed_int = int(np.sum(seed_array * 1000) % 2**31)
  return generate_key(model_path, seed=seed_int, device=device)
