# mnist_key_generator.py
import torch
import numpy as np
from key_management.autoencoder_keygen import AutoencoderKeygen
from torchvision import datasets, transforms
import hashlib

class MNISTKeyGenerator:
    def __init__(self, model_path, mnist_data_path, device='cpu'):
        self.device = device
        self.model_path = model_path

        # Load the trained autoencoder
        self.keygen = AutoencoderKeygen(model_path, input_dim=784, latent_dim=32, device=device)
        self.keygen.load_model(model_path)

        # Load MNIST dataset
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.view(-1))  # Flatten to 784
        ])

        self.mnist_dataset = datasets.MNIST(
            root=mnist_data_path,
            train=True,
            download=False,
            transform=transform
        )

        print(f"✅ MNIST Key Generator initialized with {len(self.mnist_dataset)} samples")

    def generate_key_from_digit(self, digit_value, sample_index=0):
        # Find all samples of the requested digit
        digit_indices = [i for i, (_, label) in enumerate(self.mnist_dataset)
                        if label == digit_value]

        if not digit_indices:
            raise ValueError(f"No samples found for digit {digit_value}")

        # Select the specific sample
        selected_idx = digit_indices[sample_index % len(digit_indices)]
        mnist_image, label = self.mnist_dataset[selected_idx]

        # Encode through autoencoder
        self.keygen.model.eval()
        with torch.no_grad():
            mnist_tensor = mnist_image.unsqueeze(0).to(self.device)
            latent_vector = self.keygen.model.encoder(mnist_tensor)
            key_vector = latent_vector.squeeze().cpu().numpy()

        # Convert to key
        key_bytes = (np.abs(key_vector) * 255).astype(np.uint8).tobytes()
        key_hex = key_bytes.hex()

        metadata = {
            'digit': digit_value,
            'sample_index': sample_index,
            'dataset_index': selected_idx,
            'latent_mean': float(np.mean(key_vector)),
            'latent_std': float(np.std(key_vector)),
            'key_entropy': self._calculate_entropy(key_hex)
        }

        return key_hex, metadata

    def generate_key_from_sequence(self, digit_sequence):
        combined_latent = []

        for digit in digit_sequence:
            digit_indices = [i for i, (_, label) in enumerate(self.mnist_dataset)
                           if label == digit]

            if not digit_indices:
                raise ValueError(f"No samples found for digit {digit}")

            mnist_image, _ = self.mnist_dataset[digit_indices[0]]

            self.keygen.model.eval()
            with torch.no_grad():
                mnist_tensor = mnist_image.unsqueeze(0).to(self.device)
                latent = self.keygen.model.encoder(mnist_tensor)
                combined_latent.append(latent.squeeze().cpu().numpy())

        # Combine latent vectors
        combined_vector = np.mean(combined_latent, axis=0)

        key_bytes = (np.abs(combined_vector) * 255).astype(np.uint8).tobytes()
        key_hex = key_bytes.hex()

        metadata = {
            'digit_sequence': digit_sequence,
            'num_digits': len(digit_sequence),
            'latent_mean': float(np.mean(combined_vector)),
            'latent_std': float(np.std(combined_vector)),
            'key_entropy': self._calculate_entropy(key_hex)
        }

        return key_hex, metadata

    def generate_key_from_image_index(self, image_index):
        if image_index >= len(self.mnist_dataset):
            raise ValueError(f"Index {image_index} out of range")

        mnist_image, label = self.mnist_dataset[image_index]

        self.keygen.model.eval()
        with torch.no_grad():
            mnist_tensor = mnist_image.unsqueeze(0).to(self.device)
            latent_vector = self.keygen.model.encoder(mnist_tensor)
            key_vector = latent_vector.squeeze().cpu().numpy()

        key_bytes = (np.abs(key_vector) * 255).astype(np.uint8).tobytes()
        key_hex = key_bytes.hex()

        metadata = {
            'image_index': image_index,
            'digit_label': int(label),
            'latent_mean': float(np.mean(key_vector)),
            'latent_std': float(np.std(key_vector)),
            'key_entropy': self._calculate_entropy(key_hex)
        }

        return key_hex, metadata

    def generate_deterministic_key(self, seed_string):
        hash_obj = hashlib.sha256(seed_string.encode())
        hash_bytes = hash_obj.digest()

        # Use hash to select 4 MNIST samples
        indices = [int.from_bytes(hash_bytes[i:i+2], 'big') % len(self.mnist_dataset)
                  for i in range(0, 8, 2)]

        combined_latent = []
        labels_used = []

        for idx in indices:
            mnist_image, label = self.mnist_dataset[idx]
            labels_used.append(int(label))

            self.keygen.model.eval()
            with torch.no_grad():
                mnist_tensor = mnist_image.unsqueeze(0).to(self.device)
                latent = self.keygen.model.encoder(mnist_tensor)
                combined_latent.append(latent.squeeze().cpu().numpy())

        combined_vector = np.mean(combined_latent, axis=0)

        key_bytes = (np.abs(combined_vector) * 255).astype(np.uint8).tobytes()
        key_hex = key_bytes.hex()

        metadata = {
            'seed_string': seed_string,
            'indices_used': indices,
            'labels_used': labels_used,
            'latent_mean': float(np.mean(combined_vector)),
            'latent_std': float(np.std(combined_vector)),
            'key_entropy': self._calculate_entropy(key_hex)
        }

        return key_hex, metadata

    def _calculate_entropy(self, hex_string):
        from collections import Counter

        if not hex_string:
            return 0.0

        counts = Counter(hex_string)
        length = len(hex_string)
        entropy = -sum((count/length) * np.log2(count/length)
                      for count in counts.values())

        return float(entropy)

    def analyze_key_diversity(self, num_samples=100):
        print(f"🔍 Analyzing key diversity across {num_samples} samples per digit...")

        keys_by_digit = {i: [] for i in range(10)}
        entropies = []

        for digit in range(10):
            for sample_idx in range(num_samples):
                key_hex, metadata = self.generate_key_from_digit(digit, sample_idx)
                keys_by_digit[digit].append(key_hex)
                entropies.append(metadata['key_entropy'])

        all_keys = [key for keys in keys_by_digit.values() for key in keys]
        unique_keys = len(set(all_keys))
        total_keys = len(all_keys)

        analysis = {
            'total_keys_generated': total_keys,
            'unique_keys': unique_keys,
            'uniqueness_rate': unique_keys / total_keys,
            'avg_entropy': np.mean(entropies),
            'std_entropy': np.std(entropies),
            'min_entropy': np.min(entropies),
            'max_entropy': np.max(entropies)
        }

        print(f"✅ Analysis complete:")
        print(f"   Total keys: {total_keys}")
        print(f"   Unique keys: {unique_keys}")
        print(f"   Uniqueness rate: {analysis['uniqueness_rate']:.2%}")
        print(f"   Average entropy: {analysis['avg_entropy']:.4f}")

        return analysis
