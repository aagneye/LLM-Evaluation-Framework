import pytest
from app.core.input_validation import InputValidator
from app.core.encryption import EncryptionManager


def test_sql_injection_detection():
    """Test SQL injection detection."""
    validator = InputValidator()
    
    with pytest.raises(ValueError):
        validator.sanitize_string("SELECT * FROM users")
    
    with pytest.raises(ValueError):
        validator.sanitize_string("1' OR '1'='1")


def test_xss_detection():
    """Test XSS attack detection."""
    validator = InputValidator()
    
    with pytest.raises(ValueError):
        validator.sanitize_string("<script>alert('xss')</script>")
    
    with pytest.raises(ValueError):
        validator.sanitize_string("<iframe src='evil.com'>")


def test_valid_input():
    """Test valid input passes validation."""
    validator = InputValidator()
    
    result = validator.sanitize_string("This is a normal string")
    assert result == "This is a normal string"


def test_email_validation():
    """Test email validation."""
    validator = InputValidator()
    
    assert validator.validate_email("test@example.com") is True
    assert validator.validate_email("invalid-email") is False
    assert validator.validate_email("test@") is False


def test_encryption_decryption():
    """Test encryption and decryption."""
    manager = EncryptionManager()
    
    plaintext = "secret_api_key_12345"
    
    encrypted = manager.encrypt(plaintext)
    assert encrypted != plaintext
    
    decrypted = manager.decrypt(encrypted)
    assert decrypted == plaintext


def test_api_key_encryption():
    """Test API key encryption."""
    manager = EncryptionManager()
    
    api_key = "sk-1234567890abcdef"
    
    encrypted = manager.encrypt_api_key(api_key)
    decrypted = manager.decrypt_api_key(encrypted)
    
    assert decrypted == api_key
