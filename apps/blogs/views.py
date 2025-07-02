
from rest_framework import generics
from .models import Blog
from .serializers import BlogSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils import custom_viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response

class BlogListView(custom_viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        category_name = self.request.query_params.get('category')
        queryset = Blog.objects.all()
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': "Successfully retrieved blogs",
            'data': serializer.data
        }, status=status.HTTP_200_OK)
      
