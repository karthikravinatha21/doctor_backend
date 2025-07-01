from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, ActorPortfolioViewSet

app_name = 'movies'

router = DefaultRouter()
# router.register('', MovieViewSet)
router.register('', MovieViewSet, basename='movies')
router.register('actor-portfolio', ActorPortfolioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
