from cryptography.fernet import Fernet
import base64
import hashlib
import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class EncryptionManager:
    """Manage encryption of sensitive data."""
    
    def __init__(self):
        key = self._derive_key(settings.secret_key)
        self.cipher = Fernet(key)
    
    @staticmethod
    def _derive_key(secret: str) -> bytes:
        """Derive a Fernet key from secret."""
        hash_obj = hashlib.sha256(secret.encode())
        return base64.urlsafe_b64encode(hash_obj.digest())
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string.
        
        Args:
            ciphertext: Encrypted string
            
        Returns:
            Decrypted plaintext
        """
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key for storage."""
        return self.encrypt(api_key)
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt a stored API key."""
        return self.decrypt(encrypted_key)


def get_encryption_manager() -> EncryptionManager:
    """Get encryption manager instance."""
    return EncryptionManager()
