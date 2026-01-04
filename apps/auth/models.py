"""
Models for the auth app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import encrypt_api_key, decrypt_api_key


class AIIntegration(models.Model):
    """
    Model to store user AI integration settings including encrypted API keys.
    Each user can have one integration per provider.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_integrations',
        help_text="The user who owns this AI integration"
    )
    provider = models.CharField(
        max_length=100,
        help_text="AI provider name (e.g., 'openai', 'anthropic', 'google')"
    )
    encrypted_api_key = models.TextField(
        help_text="Encrypted API key for the provider"
    )
    model = models.CharField(
        max_length=100,
        help_text="Default AI model name (e.g., 'gpt-4', 'claude-3-opus')"
    )
    base_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Custom API endpoint URL (optional, for self-hosted models)"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User-friendly label/name for this integration"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this integration is currently active/enabled"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this integration was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this integration was last updated"
    )

    class Meta:
        db_table = 'ai_integration'
        unique_together = [['user', 'provider']]
        indexes = [
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        provider_name = self.name or self.provider
        return f"{self.user.username} - {provider_name} ({self.provider})"

    def set_api_key(self, api_key: str):
        """
        Set the API key by encrypting it before storage.
        
        Args:
            api_key: The plaintext API key to encrypt and store
        """
        self.encrypted_api_key = encrypt_api_key(api_key)

    @property
    def decrypted_api_key(self) -> str:
        """
        Get the decrypted API key.
        
        Returns:
            The decrypted plaintext API key
            
        Raises:
            Exception: If decryption fails
        """
        return decrypt_api_key(self.encrypted_api_key)

