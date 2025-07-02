import json

from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.hospital.models import Hospital
from apps.hospital.serializers import HospitalSerializer
from apps.master_data.models import Department, AccountType, PricingMaster, Languages, AgeGroup, Skills
from apps.master_data.serializers import DepartmentSerializer, AccountTypeSerializer, AgeGroupSerializer, \
    SkillsSerializer
from apps.movies.models import ActorPortfolio, ActorPayment, PaymentTypeRate, ActorAudition, ActorAward
from apps.movies.serializers import ActorPortfolioSerializer, ActorPaymentSerializer, ActorAuditionSerializer, \
    ActorAwardSerializer, GroupSerializer, LanguagesSerializer
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.models import Group


# Create your views here.

class DoctorViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Hospital
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['name', 'description']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()


class DepartmentViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'id']

    # Fields available for search (partial match, case-insensitive)
    search_fields = ['name', 'description']

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()


class AccountTypeViewSet(custom_viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = AccountType
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    create_success_message = 'Your registration completed successfully!'
    list_success_message = 'list returned successfully!'
    retrieve_success_message = 'Information returned successfully!'
    update_success_message = 'Information updated successfully!'
    status_code = 200

    def get_permissions(self):

        if self.action == 'list':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        if self.action == 'retrieve':
            permission_classes = [AllowAny]
            return [permission() for permission in permission_classes]

        return super().get_permissions()

class ActorPortfolioViewSet(custom_viewsets.ModelViewSet):
    queryset = ActorPortfolio.objects.all()
    serializer_class = ActorPortfolioSerializer
    permission_classes = [IsUserBlockedPermission]

    create_success_message = 'created successfully!'
    list_success_message = 'Movies returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'
    status_code = 200


class ActorPaymentViewSet(custom_viewsets.ModelViewSet):
    queryset = ActorPayment.objects.all()
    serializer_class = ActorPaymentSerializer
    permission_classes = [IsUserBlockedPermission]

    create_success_message = 'created successfully!'
    list_success_message = 'Movies returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'
    status_code = 200

    def perform_create(self, serializer):
        # Perform the default create action for ActorPayment
        actor_payment = serializer.save()

        # Create or update the associated PaymentDetails table
        payment_type = self.request.data.get('payment_type', None)
        payment_type = json.loads(payment_type)
        for i in payment_type:
            i['actor_payment'] = actor_payment
            i['payment_type'] = PricingMaster.objects.filter(id=i.get('payment_type')).first()
            PaymentTypeRate.objects.create(**i)

        return actor_payment

    def perform_update(self, serializer):
        # Perform the default update action for ActorPayment
        actor_payment = serializer.save()

        payment_type = self.request.data.get('payment_type', None)
        payment_type = json.loads(payment_type)
        for i in payment_type:
            i['actor_payment'] = actor_payment
            i['payment_type'] = PricingMaster.objects.filter(id=i.get('payment_type')).first()
            pk = i.pop('id', None)
            PaymentTypeRate.objects.filter(id=pk).update(**i)

        return actor_payment

class ActorAuditionViewSet(custom_viewsets.ModelViewSet):
    queryset = ActorAudition.objects.all()
    serializer_class = ActorAuditionSerializer
    permission_classes = [AllowAny]

    create_success_message = 'created successfully!'
    list_success_message = 'Movies returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'
    status_code = 200


class ActorAwardViewSet(custom_viewsets.ModelViewSet):
    queryset = ActorAward.objects.all()
    serializer_class = ActorAwardSerializer
    permission_classes = [AllowAny]

    create_success_message = 'created successfully!'
    list_success_message = 'Movies returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'
    status_code = 200


class RolesViewSet(custom_viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny]

    list_success_message = 'Roles returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    status_code = 200

class LanguageViewSet(custom_viewsets.ModelViewSet):
    queryset = Languages.objects.filter(is_active=True).order_by('sort_order')
    serializer_class = LanguagesSerializer
    permission_classes = [AllowAny]

    list_success_message = 'Languages returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    status_code = 200

class AgeViewSet(custom_viewsets.ModelViewSet):
    queryset = AgeGroup.objects.filter(is_active=True).order_by('sort_order')
    serializer_class = AgeGroupSerializer
    permission_classes = [AllowAny]

    list_success_message = 'Age groups returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    status_code = 200

class SkillViewSet(custom_viewsets.ModelViewSet):
    queryset = Skills.objects.filter(is_active=True).order_by('sort_order')
    serializer_class = SkillsSerializer
    permission_classes = [AllowAny]

    list_success_message = 'Age groups returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    status_code = 200
