import base64
import logging
from collections.abc import Callable
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import validator
from sqlalchemy import String, Text, TypeDecorator

from src.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Base exception for encryption operations."""

    pass


import os
import base64
from typing import Any, Tuple


class EncryptionService:
    """
    Service for field-level encryption using Fernet.
    Each encryption operation uses a unique random salt.
    """

    SALT_LENGTH = 16

    def __init__(self, master_key: str | None = None):
        master_secret = master_key or settings.security.SECRET_KEY.get_secret_value()
        if isinstance(master_secret, str):
            master_secret = master_secret.encode()
        self.master_key = master_secret
        self._iterations = 100_000

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 32-byte key using PBKDF2 with provided salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, plaintext: str) -> str:
        """
        Encrypt a string with a random salt.
        Returns: base64(salt + ciphertext)
        """
        if not plaintext:
            return plaintext

        try:
            # Generate random salt for this encryption
            salt = os.urandom(self.SALT_LENGTH)
            key = self._derive_key(salt)
            fernet = Fernet(key)

            ciphertext = fernet.encrypt(plaintext.encode())

            # Prepend salt to ciphertext
            combined = salt + ciphertext
            return base64.urlsafe_b64encode(combined).decode()

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError("Failed to encrypt data") from e

    def decrypt_field(self, encrypted_data: str) -> str:
        """
        Decrypt data encrypted with encrypt_field.
        """
        if not encrypted_data:
            return encrypted_data

        try:
            combined = base64.urlsafe_b64decode(encrypted_data.encode())

            # Extract salt and ciphertext
            salt = combined[: self.SALT_LENGTH]
            ciphertext = combined[self.SALT_LENGTH :]

            key = self._derive_key(salt)
            fernet = Fernet(key)

            return fernet.decrypt(ciphertext).decode()

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise EncryptionError("Failed to decrypt data") from e

    def encrypt_dict(self, data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        """Recursively encrypt specified fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and isinstance(result[field], str):
                result[field] = self.encrypt_field(result[field])
        return result

    def decrypt_dict(self, data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        """Recursively decrypt specified fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and isinstance(result[field], str):
                result[field] = self.decrypt_field(result[field])
        return result

    def rotate_key(self, old_key: str, new_key: str, ciphertext: str) -> str:
        """Decrypt with old key and re-encrypt with new key."""
        old_service = EncryptionService(master_key=old_key)
        new_service = EncryptionService(master_key=new_key)
        return new_service.encrypt_field(old_service.decrypt_field(ciphertext))


# Singleton instance
encryption_service = EncryptionService()


# Backward compatibility aliases
def encrypt_data(data: str) -> str:
    return encryption_service.encrypt_field(data)


def decrypt_data(encrypted_data: str) -> str:
    return encryption_service.decrypt_field(encrypted_data)


class EncryptedString(TypeDecorator[str]):
    """SQLAlchemy type for transparent field-level encryption."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, _dialect: Any) -> Any:
        if value is not None:
            return encryption_service.encrypt_field(value)
        return value

    def process_result_value(self, value: Any, _dialect: Any) -> Any:
        if value is not None:
            return encryption_service.decrypt_field(value)
        return value


def encrypted_pydantic_validator(field_name: str) -> Callable[..., Any]:
    """Pydantic validator factory for encrypted fields if needed at schema level."""

    def validate(_cls: Any, v: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        return v

    return validator(field_name, allow_reuse=True)(validate)
