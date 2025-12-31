from django.urls import path
from .endpoints import test, protected
from apps.auth.endpoints import login
from apps.recipe.endpoints import recipes

urlpatterns = [
    path('test/', test.test_endpoint, name='test'),
    path('login/', login.login_endpoint, name='login'),
    path('protected/', protected.protected_endpoint, name='protected'),
    path('recipes/', recipes.list_or_create, name='recipes-list-create'),
    path('recipes/<str:recipe_id>/', recipes.detail_update_delete, name='recipes-detail-update-delete'),
]

