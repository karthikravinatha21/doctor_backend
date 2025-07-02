from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, AccountTypeViewSet, ActorPortfolioViewSet, ActorPaymentViewSet, \
    ActorAuditionViewSet, ActorAwardViewSet, RolesViewSet, LanguageViewSet, AgeViewSet, SkillViewSet, DoctorViewSet

app_name = 'master_data'

router = DefaultRouter()
# router.register('department', DepartmentViewSet)
router.register('doctors', DoctorViewSet)
router.register('account-type', AccountTypeViewSet)
router.register('actor-portfolio', ActorPortfolioViewSet)
router.register('actor-payments', ActorPaymentViewSet, basename='actor-payments')
router.register('actor-audition', ActorAuditionViewSet, basename='actor-audition')
router.register('actor-award', ActorAwardViewSet, basename='actor-award')
router.register('roles', RolesViewSet, basename='roles')
router.register('languages', LanguageViewSet, basename='languages')
router.register('age-group', AgeViewSet, basename='age-group')
router.register('skills', SkillViewSet, basename='skills')
urlpatterns = [
    *router.urls
]
