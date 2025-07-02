from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet

# app_name = 'budget'

router = DefaultRouter()
router.register(r'budget', BudgetViewSet)

urlpatterns = [
    *router.urls
]
