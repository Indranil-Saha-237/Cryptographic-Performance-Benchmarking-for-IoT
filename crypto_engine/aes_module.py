# aes_module.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from evaluation.resource_monitor import ResourceMonitor
from evaluation.security_metrics import SecurityMetrics


class AESCrypto:
    def __init__(self, key_size=256):
        """Initialize AES with specified key size (128, 192, or 256 bits)"""
        self.key_size = key_size // 8  # Convert bits to bytes

        # ✅ Initialize monitor and security objects
        self.monitor = ResourceMonitor()
        self.security = SecurityMetrics()


    def _prepare_key(self, key_hex):
        """Convert hex key to proper byte length for AES"""
        key_bytes = bytes.fromhex(key_hex)
        hashed = hashlib.sha256(key_bytes).digest()
        return hashed[:self.key_size]


    def encrypt(self, plaintext, key_hex):
        """Encrypt plaintext using AES-CBC"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        key = self._prepare_key(key_hex)
        iv = get_random_bytes(16)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

        return (iv + ciphertext).hex()


    def decrypt(self, ciphertext_hex, key_hex):
        """Decrypt ciphertext using AES-CBC"""
        key = self._prepare_key(key_hex)
        ciphertext_bytes = bytes.fromhex(ciphertext_hex)

        iv = ciphertext_bytes[:16]
        ciphertext = ciphertext_bytes[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        return plaintext


    def encrypt_with_metrics(self, plaintext, keyhex):
        """Encrypt with comprehensive metrics collection"""
        self.monitor.start_monitoring()

        start_time = time.perf_counter()
        ciphertext = self.encrypt(plaintext, keyhex)
        enc_time = time.perf_counter() - start_time

        resources = self.monitor.stop_monitoring()
        entropy = self.security.calculate_entropy(ciphertext)

        plaintext_size = len(plaintext) if isinstance(plaintext, bytes) else len(plaintext.encode('utf-8'))
        ciphertext_size = len(bytes.fromhex(ciphertext))
        iv_size = 16
        tag_size = 0

        import inspect
        code_size = len(inspect.getsource(AESCrypto))

        return {
            'ciphertext': ciphertext,
            'encryption_time': enc_time,
            'plaintext_size': plaintext_size,
            'ciphertext_size': ciphertext_size,
            'cpu_cycles': resources['cpu_cycles'],
            'cycles_per_byte': resources['cpu_cycles'] / plaintext_size if plaintext_size > 0 else 0,
            'memory_usage_kb': resources['memory_usage_kb'],
            'power_consumption_mw': resources['power_consumption_mw'],
            'code_size_bytes': code_size,
            'iv_size': iv_size,
            'tag_size': tag_size,
            'total_overhead': iv_size + tag_size,
            'entropy_score': entropy
        }

    def decrypt_with_metrics(self, ciphertexthex, keyhex):
        """Decrypt with comprehensive metrics"""
        self.monitor.start_monitoring()

        start_time = time.perf_counter()
        plaintext = self.decrypt(ciphertexthex, keyhex)
        dec_time = time.perf_counter() - start_time

        resources = self.monitor.stop_monitoring()

        return {
            'plaintext': plaintext,
            'decryption_time': dec_time,
            'cpu_cycles': resources['cpu_cycles'],
            'memory_usage_kb': resources['memory_usage_kb'],
            'power_consumption_mw': resources['power_consumption_mw']
        }


# Standalone functions for backward compatibility
def encrypt_data(data, key_hex):
    aes = AESCrypto()
    return aes.encrypt(data, key_hex)

def decrypt(ciphertext_hex, key_hex):
    aes = AESCrypto()
    return aes.decrypt(ciphertext_hex, key_hex)
