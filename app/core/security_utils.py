from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Generate a key if not present for development/testing, but warn in production
    # In a real scenario, this should raise an error or be handled gracefully
    pass

def get_fernet():
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY environment variable is not set")
    return Fernet(ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    """Encrypts a token string."""
    f = get_fernet()
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts an encrypted token string."""
    f = get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()
