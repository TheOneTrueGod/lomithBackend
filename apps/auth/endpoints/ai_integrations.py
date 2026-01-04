"""
AI Integrations API endpoint.
Handles HTTP requests and responses for AI integration operations.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.auth.models import AIIntegration
from apps.auth.utils import (
    detect_provider_from_api_key,
    get_default_model,
    get_default_base_url,
)


def _serialize_integration(integration: AIIntegration) -> dict:
    """
    Serialize an AIIntegration instance to a response dictionary.
    Never includes the decrypted API key for security.
    
    Args:
        integration: The AIIntegration instance to serialize
        
    Returns:
        Dictionary with integration data (without decrypted API key)
    """
    return {
        'id': integration.id,
        'provider': integration.provider,
        'model': integration.model,
        'base_url': integration.base_url,
        'name': integration.name,
        'is_active': integration.is_active,
        'created_at': integration.created_at.isoformat(),
        'updated_at': integration.updated_at.isoformat(),
        'has_api_key': bool(integration.encrypted_api_key),
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_or_create(request):
    """
    Handle GET (list all) or POST (create) requests for AI integrations.
    """
    if request.method == 'GET':
        return list_all(request)
    elif request.method == 'POST':
        return create(request)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def detail_update(request, provider: str):
    """
    Handle GET (get one) or PUT (update) requests for a specific AI integration.
    """
    if request.method == 'GET':
        return get_by_provider(request, provider)
    elif request.method == 'PUT':
        return update(request, provider)


def list_all(request):
    """
    Get all AI integrations for the authenticated user.
    
    Returns:
        Response with list of integrations
    """
    try:
        integrations = AIIntegration.objects.filter(user=request.user)
        serialized = [_serialize_integration(integration) for integration in integrations]
        
        return Response(
            {'integrations': serialized},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve integrations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_by_provider(request, provider: str):
    """
    Get a specific AI integration by provider for the authenticated user.
    
    Args:
        request: The HTTP request
        provider: The provider name
        
    Returns:
        Response with integration data or 404 if not found
    """
    try:
        integration = get_object_or_404(
            AIIntegration,
            user=request.user,
            provider=provider.lower()
        )
        
        return Response(
            _serialize_integration(integration),
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve integration: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def create(request):
    """
    Create a new AI integration for the authenticated user.
    
    Request Body (all optional except api_key):
        - api_key (string, required): The API key to encrypt and store
        - provider (string, optional): Auto-detected from API key if not provided
        - model (string, optional): Defaults to provider's default model
        - base_url (string, optional): Defaults to provider's default URL
        - name (string, optional): Defaults to provider name
        - is_active (boolean, optional): Defaults to true
        
    Returns:
        Response with created integration data
    """
    try:
        # Extract required field
        api_key = request.data.get('api_key', '').strip()
        if not api_key:
            return Response(
                {'error': 'api_key is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Determine provider
        provider = request.data.get('provider', '').strip()
        if not provider:
            provider = detect_provider_from_api_key(api_key)
        
        if not provider:
            return Response(
                {'error': 'provider is required and could not be auto-detected from API key'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        provider = provider.lower()
        
        # Get or create integration (update if exists due to unique constraint)
        integration, created = AIIntegration.objects.get_or_create(
            user=request.user,
            provider=provider,
            defaults={
                'model': request.data.get('model', '').strip() or get_default_model(provider),
                'base_url': request.data.get('base_url', '').strip() or get_default_base_url(provider),
                'name': request.data.get('name', '').strip() or provider,
                'is_active': request.data.get('is_active', True),
            }
        )
        
        # Always set API key (encrypts automatically)
        integration.set_api_key(api_key)
        
        # Update fields if integration already existed or if fields were explicitly provided
        if not created or 'model' in request.data:
            model_value = request.data.get('model', '').strip()
            integration.model = model_value if model_value else get_default_model(provider)
        
        if not created or 'base_url' in request.data:
            base_url_value = request.data.get('base_url', '').strip()
            integration.base_url = base_url_value if base_url_value else get_default_base_url(provider)
        
        if not created or 'name' in request.data:
            name_value = request.data.get('name', '').strip()
            integration.name = name_value if name_value else provider
        
        if not created or 'is_active' in request.data:
            integration.is_active = request.data.get('is_active', True)
        
        integration.save()
        
        return Response(
            _serialize_integration(integration),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create integration: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def update(request, provider: str):
    """
    Update an existing AI integration for the authenticated user.
    
    Args:
        request: The HTTP request
        provider: The provider name
        
    Request Body (all optional):
        - api_key (string, optional): Update API key if provided
        - model (string, optional): Update model
        - base_url (string, optional): Update base URL
        - name (string, optional): Update name
        - is_active (boolean, optional): Update active status
        
    Returns:
        Response with updated integration data or 404 if not found
    """
    try:
        integration = get_object_or_404(
            AIIntegration,
            user=request.user,
            provider=provider.lower()
        )
        
        # Update API key if provided
        if 'api_key' in request.data:
            api_key = request.data.get('api_key', '').strip()
            if api_key:
                integration.set_api_key(api_key)
        
        # Update other fields if provided
        if 'model' in request.data:
            integration.model = request.data.get('model', '').strip()
        
        if 'base_url' in request.data:
            base_url = request.data.get('base_url', '').strip()
            integration.base_url = base_url if base_url else None
        
        if 'name' in request.data:
            name = request.data.get('name', '').strip()
            integration.name = name if name else None
        
        if 'is_active' in request.data:
            integration.is_active = request.data.get('is_active', True)
        
        integration.save()
        
        return Response(
            _serialize_integration(integration),
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update integration: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

