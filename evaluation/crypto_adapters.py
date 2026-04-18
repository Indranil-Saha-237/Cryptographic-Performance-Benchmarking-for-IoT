"""
Crypto Module Adapters for Security Testing
Bridges the interface between your hex-string-based crypto modules
and the security robustness tests that use raw bytes.
"""

from crypto_engine.aes_module import AESCrypto
from crypto_engine.ascon_module import AsconCrypto


class AESAdapter:
    """
    Adapter to make AESCrypto compatible with security tests.
    Converts between raw bytes and hex strings automatically.
    """
    
    def __init__(self, key_size=256):
        self.aes = AESCrypto(key_size=key_size)
        self.key_size = key_size
    
    def encrypt(self, plaintext, key):
        """
        Encrypt data with automatic key/output format conversion
        
        Args:
            plaintext (bytes or str): Data to encrypt
            key (bytes or str): Encryption key
        
        Returns:
            bytes: Encrypted ciphertext (raw bytes)
        """
        # Convert bytes key to hex string if necessary
        if isinstance(key, bytes):
            key_hex = key.hex()
        else:
            key_hex = key
        
        # Encrypt (returns hex string)
        ciphertext_hex = self.aes.encrypt(plaintext, key_hex)
        
        # DEBUG: Check what type we got
        if not isinstance(ciphertext_hex, str):
            raise TypeError(f"AES.encrypt should return str, got {type(ciphertext_hex)}")
        
        # Convert hex string back to bytes for security tests
        result = bytes.fromhex(ciphertext_hex)
        
        # VERIFY: Make sure we're returning bytes
        if not isinstance(result, bytes):
            raise TypeError(f"Conversion failed: expected bytes, got {type(result)}")
        
        return result
    
    def decrypt(self, ciphertext, key):
        """
        Decrypt data with automatic key/input format conversion
        
        Args:
            ciphertext (bytes or str): Encrypted data
            key (bytes or str): Decryption key
        
        Returns:
            bytes: Decrypted plaintext (raw bytes)
        """
        # Convert bytes key to hex string if necessary
        if isinstance(key, bytes):
            key_hex = key.hex()
        else:
            key_hex = key
        
        # Convert bytes ciphertext to hex string if necessary
        if isinstance(ciphertext, bytes):
            ciphertext_hex = ciphertext.hex()
        else:
            ciphertext_hex = ciphertext
        
        # Decrypt (returns bytes or str depending on implementation)
        plaintext = self.aes.decrypt(ciphertext_hex, key_hex)
        
        # Ensure bytes output
        if isinstance(plaintext, str):
            return plaintext.encode('utf-8')
        else:
            return plaintext


class AsconAdapter:
    """
    Adapter to make AsconCrypto compatible with security tests.
    Converts between raw bytes and hex strings automatically.
    """
    
    def __init__(self):
        self.ascon = AsconCrypto()
    
    def encrypt(self, plaintext, key, associated_data=b""):
        """
        Encrypt data with ASCON and automatic format conversion
        
        Args:
            plaintext (bytes or str): Data to encrypt
            key (bytes or str): Encryption key
            associated_data (bytes): Additional authenticated data
        
        Returns:
            bytes: Encrypted ciphertext with authentication tag (raw bytes)
        """
        # Convert bytes key to hex string if necessary
        if isinstance(key, bytes):
            key_hex = key.hex()
        else:
            key_hex = key
        
        # Encrypt (returns hex string)
        ciphertext_hex = self.ascon.encrypt(plaintext, key_hex, associated_data)
        
        # DEBUG: Check what type we got
        if not isinstance(ciphertext_hex, str):
            raise TypeError(f"ASCON.encrypt should return str, got {type(ciphertext_hex)}")
        
        # Convert hex string back to bytes for security tests
        result = bytes.fromhex(ciphertext_hex)
        
        # VERIFY: Make sure we're returning bytes
        if not isinstance(result, bytes):
            raise TypeError(f"Conversion failed: expected bytes, got {type(result)}")
        
        return result
    
    def decrypt(self, ciphertext, key, associated_data=b""):
        """
        Decrypt data with ASCON and automatic format conversion
        
        Args:
            ciphertext (bytes or str): Encrypted data with authentication tag
            key (bytes or str): Decryption key
            associated_data (bytes): Additional authenticated data
        
        Returns:
            bytes: Decrypted plaintext (raw bytes)
        """
        # Convert bytes key to hex string if necessary
        if isinstance(key, bytes):
            key_hex = key.hex()
        else:
            key_hex = key
        
        # Convert bytes ciphertext to hex string if necessary
        if isinstance(ciphertext, bytes):
            ciphertext_hex = ciphertext.hex()
        else:
            ciphertext_hex = ciphertext
        
        # Decrypt (returns bytes or str depending on implementation)
        plaintext = self.ascon.decrypt(ciphertext_hex, key_hex, associated_data)
        
        # Ensure bytes output
        if isinstance(plaintext, str):
            return plaintext.encode('utf-8')
        else:
            return plaintext


# Convenience function for quick testing
def test_adapters():
    """Quick test to verify adapters work correctly"""
    import os
    
    print("Testing Crypto Adapters...")
    
    # Test AES
    try:
        aes = AESAdapter(key_size=256)
        key = os.urandom(32)
        plaintext = b"Hello, World! This is a test."
        
        ciphertext = aes.encrypt(plaintext, key)
        
        # Verify ciphertext is bytes
        if not isinstance(ciphertext, bytes):
            raise TypeError(f"AES encrypt should return bytes, got {type(ciphertext)}")
        
        recovered = aes.decrypt(ciphertext, key)
        
        # Verify recovered is bytes
        if not isinstance(recovered, bytes):
            raise TypeError(f"AES decrypt should return bytes, got {type(recovered)}")
        
        aes_pass = (recovered == plaintext)
        print(f"  AES-256 Adapter: {'✓ PASSED' if aes_pass else '✗ FAILED'}")
        
        if not aes_pass:
            print(f"    Expected: {plaintext}")
            print(f"    Got: {recovered}")
            
    except Exception as e:
        print(f"  AES-256 Adapter: ✗ FAILED - {e}")
        import traceback
        traceback.print_exc()
        aes_pass = False
    
    # Test ASCON
    try:
        ascon = AsconAdapter()
        key = os.urandom(16)
        plaintext = b"Hello, World! This is a test."
        
        ciphertext = ascon.encrypt(plaintext, key)
        
        # Verify ciphertext is bytes
        if not isinstance(ciphertext, bytes):
            raise TypeError(f"ASCON encrypt should return bytes, got {type(ciphertext)}")
        
        recovered = ascon.decrypt(ciphertext, key)
        
        # Verify recovered is bytes
        if not isinstance(recovered, bytes):
            raise TypeError(f"ASCON decrypt should return bytes, got {type(recovered)}")
        
        ascon_pass = (recovered == plaintext)
        print(f"  ASCON-128 Adapter: {'✓ PASSED' if ascon_pass else '✗ FAILED'}")
        
        if not ascon_pass:
            print(f"    Expected: {plaintext}")
            print(f"    Got: {recovered}")
            
    except Exception as e:
        print(f"  ASCON-128 Adapter: ✗ FAILED - {e}")
        import traceback
        traceback.print_exc()
        ascon_pass = False
    
    if aes_pass and ascon_pass:
        print("\n✓ All adapter tests passed! Ready for security testing.")
    else:
        print("\n⚠ Some adapter tests failed. Check crypto module implementations.")
    
    return aes_pass and ascon_pass


if __name__ == "__main__":
    test_adapters()
