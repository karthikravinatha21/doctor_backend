from rest_framework import viewsets, status
from rest_framework.response import Response

from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import Movie, ActorPortfolio, ActorAward, ActorAudition, ActorPayment
from .serializers import MovieSerializer, ActorPortfolioSerializer, ActorAwardSerializer, ActorAuditionSerializer, \
    ActorPaymentSerializer


class MovieViewSet(custom_viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsUserBlockedPermission]  # Add custom permissions if needed

    create_success_message = 'Movie created successfully!'
    list_success_message = 'List of movies returned successfully!'
    retrieve_success_message = 'Movie information returned successfully!'
    update_success_message = 'Movie updated successfully!'
    destroy_success_message = 'Movie deleted successfully!'

    # Custom create method
    def create(self, request, *args, **kwargs):
        # Use the MovieSerializer to validate and create a new movie instance
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the movie instance
            movie = serializer.save()
            return Response({
                'message': self.create_success_message,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Custom list method (to retrieve a list of all movies)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': self.list_success_message,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    # Custom retrieve method (to get a specific movie by ID)
    def retrieve(self, request, *args, **kwargs):
        movie = self.get_object()  # Get the movie by primary key (id)
        serializer = self.get_serializer(movie)
        return Response({
            'message': self.retrieve_success_message,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        movie = self.get_object()  # Get the movie instance by ID
        serializer = self.get_serializer(movie, data=request.data, partial=False)  # Validate incoming data
        if serializer.is_valid():
            movie = serializer.save()  # Save the updated movie instance
            return Response({
                'message': self.update_success_message,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Custom destroy method (to delete a movie by ID)
    def destroy(self, request, *args, **kwargs):
        movie = self.get_object()  # Get the movie instance by ID
        movie.delete()  # Delete the movie
        return Response({
            'message': self.destroy_success_message
        }, status=status.HTTP_204_NO_CONTENT)


class ActorPortfolioViewSet(viewsets.ModelViewSet):
    queryset = ActorPortfolio.objects.all()
    serializer_class = ActorPortfolioSerializer
    permission_classes = [IsUserBlockedPermission]

    create_success_message = 'created successfully!'
    list_success_message = 'Movies returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'

    def create(self, request, *args, **kwargs):
        """
        Handle POST request for creating a new Actor Portfolio.
        """
        # You can add any custom logic here if needed before creating the portfolio
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Save the new Actor Portfolio object
            serializer.save()
            return Response({
                'message': self.create_success_message,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Handle PUT request for updating an existing Actor Portfolio.
        """
        # Fetch the existing Actor Portfolio object by its ID
        instance = self.get_object()

        # Create a serializer instance with the data to update the portfolio
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=False)  # set partial=True if you want partial updates

        if serializer.is_valid():
            # Save the updated Actor Portfolio object
            serializer.save()
            return Response({
                'message': self.update_success_message,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


