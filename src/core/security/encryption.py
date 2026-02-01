import base64
import logging
from collections.abc import Callable
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import validator
from sqlalchemy import String, TypeDecorator

from src.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Base exception for encryption operations."""

    pass


class EncryptionService:
    """Service for field-level encryption using Fernet and PBKDF2 key derivation."""

    def __init__(self, master_key: str | None = None):
        master_secret = (master_key or settings.security.SECRET_KEY).encode()
        self.master_key = master_secret
        self._iterations = 100_000
        # For simple field encryption, we use a fixed salt for deterministic
        # derivation if needed, but standard Fernet handles its own IV/Salt
        # per message. Here we derive a stable key for the Fernet instance.
        self._key = self._derive_key(b"stellapply-static-salt")
        self._fernet = Fernet(self._key)

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 32-byte key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded ciphertext."""
        if not plaintext:
            return plaintext
        try:
            return self._fernet.encrypt(plaintext.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise EncryptionError("Failed to encrypt data") from e

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a base64 encoded ciphertext."""
        if not ciphertext:
            return ciphertext
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
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

    impl = String
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
