from django.urls import path
from .views import dynamic_page, home_page


# router = DefaultRouter()
# router.register('api/appauth', AppUserView, basename='api/appauth')
urlpatterns = [
    path('<slug:slug>', dynamic_page, name='dynamic_page'),
    path('', home_page, name='home_page'),
]
