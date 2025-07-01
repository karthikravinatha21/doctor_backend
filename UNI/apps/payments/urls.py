from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('payment', RazorpayView, basename='payment')
router.register('subscription', SubscriptionView, basename='subscription')
urlpatterns = [
    *router.urls
]
