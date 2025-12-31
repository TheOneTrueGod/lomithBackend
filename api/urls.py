from django.urls import path
from .endpoints import test, login, protected
from apps.recipe.endpoints import recipes

urlpatterns = [
    path('test/', test.test_endpoint, name='test'),
    path('login/', login.login_endpoint, name='login'),
    path('protected/', protected.protected_endpoint, name='protected'),
    path('recipes/', recipes.get_list, name='recipes-list'),
]

