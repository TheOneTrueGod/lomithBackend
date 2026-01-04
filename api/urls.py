from django.urls import path
from .endpoints import test, protected
from apps.auth.endpoints import login, create_user, ai_integrations
from apps.recipe.endpoints import recipes

urlpatterns = [
    path('test/', test.test_endpoint, name='test'),
    path('login/', login.login_endpoint, name='login'),
    path('create-user/', create_user.create_user_endpoint, name='create-user'),
    path('protected/', protected.protected_endpoint, name='protected'),
    path('recipes/', recipes.list_or_create, name='recipes-list-create'),
    path('recipes/<str:recipe_id>/', recipes.detail_update_delete, name='recipes-detail-update-delete'),
    path('ai-integrations/', ai_integrations.list_or_create, name='ai-integrations-list'),
    path('ai-integrations/<str:provider>/', ai_integrations.detail_update, name='ai-integrations-detail'),
]

