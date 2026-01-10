"""
Encryption utilities for securely storing API keys.
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings


def _get_encryption_key():
    """
    Derive a Fernet encryption key from Django's SECRET_KEY.
    Fernet requires a 32-byte key, so we hash the SECRET_KEY to get the right length.
    """
    secret_key = settings.SECRET_KEY.encode('utf-8')
    # Use SHA256 to get a 32-byte key suitable for Fernet
    key = hashlib.sha256(secret_key).digest()
    # Fernet expects a URL-safe base64-encoded 32-byte key
    key_b64 = base64.urlsafe_b64encode(key)
    return Fernet(key_b64)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key using Fernet symmetric encryption.
    
    Args:
        api_key: The plaintext API key to encrypt
        
    Returns:
        The encrypted API key as a string
    """
    if not api_key:
        return ""
    
    fernet = _get_encryption_key()
    encrypted = fernet.encrypt(api_key.encode('utf-8'))
    return encrypted.decode('utf-8')


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an API key that was encrypted with encrypt_api_key.
    
    Args:
        encrypted_key: The encrypted API key string
        
    Returns:
        The decrypted plaintext API key
        
    Raises:
        Exception: If decryption fails (invalid key or corrupted data)
    """
    if not encrypted_key:
        return ""
    
    fernet = _get_encryption_key()
    decrypted = fernet.decrypt(encrypted_key.encode('utf-8'))
    return decrypted.decode('utf-8')


def detect_provider_from_api_key(api_key: str) -> str | None:
    """
    Auto-detect AI provider from API key format.
    
    Args:
        api_key: The API key string
        
    Returns:
        Provider name (e.g., 'openai', 'anthropic', 'google') or None if cannot detect
    """
    if not api_key:
        return None
    
    api_key_lower = api_key.lower().strip()
    
    # Anthropic keys start with "sk-ant-"
    if api_key_lower.startswith('sk-ant-'):
        return 'anthropic'
    
    # OpenAI keys start with "sk-"
    if api_key_lower.startswith('sk-'):
        return 'openai'
    
    # Google/Gemini API keys are typically longer and may have different patterns
    # Common patterns: AIza... (for API keys) or service account JSON keys
    if api_key_lower.startswith('aiza') or len(api_key) > 100:
        return 'google'
    
    return None


def get_default_model(provider: str) -> str:
    """
    Get the default AI model for a given provider.
    
    Args:
        provider: The provider name (e.g., 'openai', 'anthropic', 'google')
        
    Returns:
        Default model name for the provider, or 'gpt-4' as fallback
    """
    defaults = {
        'openai': 'gpt-4',
        'anthropic': 'claude-3-opus',
        'google': 'gemini-2.5-flash',  # Updated: gemini-pro is deprecated
    }
    
    provider_lower = provider.lower() if provider else ''
    return defaults.get(provider_lower, 'gpt-4')


def get_default_base_url(provider: str) -> str | None:
    """
    Get the default base URL for a given provider.
    
    Args:
        provider: The provider name (e.g., 'openai', 'anthropic', 'google')
        
    Returns:
        Default base URL for the provider, or None if no default
    """
    defaults = {
        'openai': 'https://api.openai.com/v1',
        'anthropic': 'https://api.anthropic.com/v1',
        'google': 'https://generativelanguage.googleapis.com/v1',
    }
    
    provider_lower = provider.lower() if provider else ''
    return defaults.get(provider_lower, None)

