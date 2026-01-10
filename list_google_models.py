"""
Script to list available Google AI models using the ListModels API.
Run this script to see what models are available for your API key.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import google.generativeai as genai
from apps.auth.models import AIIntegration
from django.contrib.auth.models import User


def list_google_models(api_key=None):
    """
    List all available Google AI models.
    
    Args:
        api_key: Optional API key. If not provided, will try to get from database.
    """
    # If API key not provided, try to get from database
    if not api_key:
        try:
            # Get the first Google integration from the database
            integration = AIIntegration.objects.filter(provider='google', is_active=True).first()
            if integration:
                api_key = integration.decrypted_api_key
                print(f"Using API key from integration: {integration.name or integration.provider}")
            else:
                print("No Google integration found in database.")
                print("Please provide an API key as an argument or create a Google integration first.")
                return
        except Exception as e:
            print(f"Error getting API key from database: {e}")
            return
    
    if not api_key:
        print("Error: No API key provided or found.")
        return
    
    # Configure the API key
    genai.configure(api_key=api_key)
    
    print("\n" + "="*80)
    print("Available Google AI Models")
    print("="*80 + "\n")
    
    try:
        # List all models
        models = genai.list_models()
        
        # Filter models that support generateContent
        generate_content_models = []
        for model in models:
            # Check if the model supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                generate_content_models.append(model)
        
        if not generate_content_models:
            print("No models found that support generateContent.")
            print("\nAll available models:")
            for model in models:
                print(f"  - {model.name}")
                print(f"    Supported methods: {', '.join(model.supported_generation_methods)}")
                print(f"    Display name: {model.display_name}")
                print()
        else:
            print(f"Found {len(generate_content_models)} model(s) that support generateContent:\n")
            for model in generate_content_models:
                print(f"Model Name: {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description}")
                print(f"  Supported Methods: {', '.join(model.supported_generation_methods)}")
                if hasattr(model, 'input_token_limit'):
                    print(f"  Input Token Limit: {model.input_token_limit}")
                if hasattr(model, 'output_token_limit'):
                    print(f"  Output Token Limit: {model.output_token_limit}")
                print()
        
        print("="*80)
        print("\nRecommended models for generateContent:")
        for model in generate_content_models:
            # Look for common Gemini model names
            if 'gemini' in model.name.lower():
                print(f"  - {model.name}")
        
    except Exception as e:
        print(f"Error listing models: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if API key provided as command line argument
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    list_google_models(api_key)

