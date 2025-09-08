import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Generate or load encryption key
def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate key from password and salt
        password = os.getenv("ENCRYPTION_PASSWORD", "default-therapy-bot-key").encode()
        salt = os.getenv("ENCRYPTION_SALT", "therapy-bot-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
    else:
        key = key.encode()
    
    return key

# Initialize Fernet cipher
_cipher = Fernet(get_encryption_key())

def encrypt_data(plaintext: str) -> str:
    """Encrypt plaintext data using Fernet symmetric encryption"""
    if not plaintext:
        return plaintext
    return _cipher.encrypt(plaintext.encode()).decode()

def decrypt_data(ciphertext: str) -> str:
    """Decrypt ciphertext data using Fernet symmetric encryption"""
    if not ciphertext:
        return ciphertext
    try:
        return _cipher.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ciphertext  # Return as-is if decryption fails

# Legacy aliases for backward compatibility
encrypt_field = encrypt_data
decrypt_field = decrypt_data