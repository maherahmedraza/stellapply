import base64

from cryptography.fernet import Fernet

from src.core.config import settings


# In a real app, generate a proper key and store it in environment variables
def get_encryption_key() -> bytes:
    # Fernet requires a 32-byte base64 encoded string
    key = settings.security.SECRET_KEY.ljust(32)[:32].encode()
    return base64.urlsafe_b64encode(key)


_fernet = Fernet(get_encryption_key())


def encrypt_data(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    return _fernet.decrypt(encrypted_data.encode()).decode()
