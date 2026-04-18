# ascon_module.py
import ascon
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from evaluation.resource_monitor import ResourceMonitor
from evaluation.security_metrics import SecurityMetrics


class AsconCrypto:
    def __init__(self, variant='Ascon-128'):
        """Initialize ASCON with specified variant"""
        self.variant = variant
        self.key_size = 16
        self.nonce_size = 16

        # ✅ Initialize monitor and security objects
        self.monitor = ResourceMonitor()
        self.security = SecurityMetrics()


    def encrypt(self, plaintext, key_hex, associated_data=b''):
        """Encrypt plaintext using ASCON AEAD"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        key = bytes.fromhex(key_hex)[:self.key_size]

        import secrets
        nonce = secrets.token_bytes(self.nonce_size)

        ciphertext = ascon.encrypt(key, nonce, associated_data, plaintext, variant="Ascon-128")

        return (nonce + ciphertext).hex()


    def decrypt(self, ciphertext_hex, key_hex, associated_data=b''):
        """Decrypt ciphertext using ASCON AEAD"""
        key = bytes.fromhex(key_hex)[:self.key_size]
        ciphertext_bytes = bytes.fromhex(ciphertext_hex)

        nonce = ciphertext_bytes[:self.nonce_size]
        ciphertext = ciphertext_bytes[self.nonce_size:]

        plaintext = ascon.decrypt(key, nonce, associated_data, ciphertext, variant="Ascon-128")

        if plaintext is None:
            raise ValueError("Ascon decryption failed")
        return plaintext


    def encrypt_with_metrics(self, plaintext, keyhex, associateddata=b''):
        """Encrypt with comprehensive metrics for research paper"""
        self.monitor.start_monitoring()

        start_time = time.perf_counter()
        ciphertext_hex = self.encrypt(plaintext, keyhex, associateddata)
        enc_time = time.perf_counter() - start_time

        resources = self.monitor.stop_monitoring()
        entropy = self.security.calculate_entropy(ciphertext_hex)

        plaintext_size = len(plaintext) if isinstance(plaintext, bytes) else len(plaintext.encode('utf-8'))
        ciphertext_size = len(bytes.fromhex(ciphertext_hex))
        nonce_size = 16
        tag_size = 16
        aad_size = len(associateddata)

        import inspect
        code_size = len(inspect.getsource(AsconCrypto))

        return {
            'ciphertext': ciphertext_hex,
            'encryption_time': enc_time,
            'plaintext_size': plaintext_size,
            'ciphertext_size': ciphertext_size,
            'cpu_cycles': resources['cpu_cycles'],
            'cycles_per_byte': resources['cpu_cycles'] / plaintext_size if plaintext_size > 0 else 0,
            'memory_usage_kb': resources['memory_usage_kb'],
            'power_consumption_mw': resources['power_consumption_mw'],
            'code_size_bytes': code_size,
            'nonce_size': nonce_size,
            'tag_size': tag_size,
            'aad_size': aad_size,
            'total_overhead': nonce_size + tag_size + aad_size,
            'overhead_percent': (nonce_size + tag_size + aad_size) / plaintext_size * 100 if plaintext_size > 0 else 0,
            'entropy_score': entropy
        }

    def decrypt_with_metrics(self, ciphertexthex, keyhex, associateddata=b''):
        """Decrypt with metrics"""
        self.monitor.start_monitoring()

        start_time = time.perf_counter()
        plaintext = self.decrypt(ciphertexthex, keyhex, associateddata)
        dec_time = time.perf_counter() - start_time

        resources = self.monitor.stop_monitoring()

        return {
            'plaintext': plaintext,
            'decryption_time': dec_time,
            'cpu_cycles': resources['cpu_cycles'],
            'memory_usage_kb': resources['memory_usage_kb'],
            'power_consumption_mw': resources['power_consumption_mw']
        }


# Standalone functions
def encrypt_data(data, key_hex, associated_data=b''):
    ascon_crypto = AsconCrypto()
    return ascon_crypto.encrypt(data, key_hex, associated_data)

def decrypt(ciphertext_hex, key_hex, associated_data=b''):
    ascon_crypto = AsconCrypto()
    return ascon_crypto.decrypt(ciphertext_hex, key_hex, associated_data)
