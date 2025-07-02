from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from user_details.models import User
from user_details.permission import IsUserBlockedPermission
from utils import custom_viewsets
from .models import Movie, Budget, MovieBudgetResource, ProductionHouse
from .serializers import BudgetSerializer, MovieBudgetResourceSerializer
from django.db import transaction


class BudgetViewSet(custom_viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsUserBlockedPermission]  # Add custom permissions if needed

    create_success_message = 'Created successfully!'
    list_success_message = 'List returned successfully!'
    retrieve_success_message = 'Data returned successfully!'
    update_success_message = 'Updated successfully!'
    destroy_success_message = 'Deleted successfully!'
    status_code = status.HTTP_200_OK

    def get_queryset(self):
        """
        This view should return a list of all the budgets for the given
        'movie=1' filter (or other custom filters).
        """
        queryset = self.queryset

        # Apply filter based on 'movie=1'
        movie = self.request.GET.get('movie', None)  # Corrected line using get() method
        if movie:
            queryset = queryset.filter(movie__id=movie)

        return queryset

    def create(self, request, *args, **kwargs):
        # Start a transaction for the creation process
        with transaction.atomic():
            # Save the movie object
            movie_id = request.data.get('movie', None)
            title = request.data.get('title', None)
            if movie_id:
                movie = Movie.objects.filter(id=movie_id).first()
            else:
                movie = Movie.objects.create(
                    title=request.data.get('title'),
                    production_house_id=request.data.get('production_house')
                )

            # Create the Budget object for the new movie
            budget = Budget.objects.create(movie=movie, production_house=movie.production_house, title=title)

            # Handle the users and resources (actors, directors, crew) and their contributions to the budget
            actors_budget = 0
            director_budget = 0
            crew_budget = 0
            marketing_budget = 0

            # Assuming 'resources' is passed in the request with role and salary information
            resources_data = request.data.get('resources', [])
            for resource in resources_data:
                user_id = resource.get('user')
                role = resource.get('role')
                salary = resource.get('salary')
                contribution = resource.get('contribution')
                # resource['user'] = User.objects.filter(id=user_id).first()
                user = User.objects.filter(id=user_id).first()
                resource['budget'] = budget
                # Create a MovieBudgetResource entry for the user
                # resource_serializer = MovieBudgetResourceSerializer(data=resource)
                # if resource_serializer.is_valid():
                #     resource_serializer.save()
                # else:
                #     # Print the serializer errors to debug
                #     print("Serializer Errors:", resource_serializer.errors)
                #     return Response(resource_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                MovieBudgetResource.objects.create(
                    user=user,
                    role=role,
                    salary=salary,
                    contribution=contribution,
                    movie_budget=budget
                )

                # Update the budget for each role
                if role == 'actor':
                    actors_budget += salary
                elif role == 'director':
                    director_budget += salary
                elif role == 'crew':
                    crew_budget += salary

            # Update the budget totals
            budget.actors_budget = actors_budget
            budget.director_budget = director_budget
            budget.crew_budget = crew_budget
            budget.marketing_budget = marketing_budget
            budget.calculate_budget()

            # Return the success response
            return Response({
                'message': self.create_success_message,
                'data': BudgetSerializer(budget).data
            }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Get the movie object to be updated
        budget_object = self.get_object()

        # Start a transaction for the update process
        with transaction.atomic():
            # Update the movie details
            budget_object.title = request.data.get('title', budget_object.title)
            budget_object.production_house_id = request.data.get('production_house', budget_object.production_house.id)
            budget_object.save()

            # Handle the users and resources (actors, directors, crew) and their contributions to the budget
            resources_data = request.data.get('resources', [])
            actors_budget = 0
            director_budget = 0
            crew_budget = 0
            marketing_budget = 0

            # Loop through resources and update or add new ones
            for resource in resources_data:
                user = resource.get('user')  # User ID
                role = resource.get('role')  # 'actor', 'director', 'crew'
                salary = resource.get('salary')  # Salary contribution

                # Find the existing resource or create a new one
                MovieBudgetResource.objects.update_or_create(user=user, movie_budget=budget_object, role=role,
                                                             defaults={'salary': salary})

                # Update the budget based on roles
                if role == 'actor':
                    actors_budget += salary
                elif role == 'director':
                    director_budget += salary
                elif role == 'crew':
                    crew_budget += salary

            # Update the budget totals
            budget_object.actors_budget = actors_budget
            budget_object.director_budget = director_budget
            budget_object.crew_budget = crew_budget
            budget_object.marketing_budget = marketing_budget  # Add marketing budget if needed
            budget_object.calculate_budget()  # Recalculate the total budget of the movie

            # Return the success response
            return Response({'message': self.update_success_message, 'data': BudgetSerializer(budget_object).data},
                            status=status.HTTP_200_OK)
