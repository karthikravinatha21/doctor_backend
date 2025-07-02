from rest_framework import generics
from .models import Event, Banner
from .serializers import EventSerializer, BannerSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils import custom_viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response

class EventListAPIView(custom_viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        category_name = self.request.query_params.get('category')
        queryset = Event.objects.all()
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': "Successfully retrieved blogs",
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class BannerListAPIView(generics.ListAPIView):
    queryset = Banner.objects.all()
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer
