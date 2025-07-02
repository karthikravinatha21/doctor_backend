from django.db import models

from apps.meta_app.models import MyBaseModel
from apps.movies.models import Movie
from apps.production_house.models import ProductionHouse
from user_details.models import User


# Create your models here.
class Budget(MyBaseModel):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='budget_movie')
    production_house = models.ForeignKey(ProductionHouse, on_delete=models.CASCADE, related_name='budget_production_house')
    title = models.CharField(max_length=256)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    actors_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    director_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    crew_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    marketing_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    is_collaborated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def calculate_budget(self):
        """
        This function calculates the total movie budget
        based on the budget contributions from actors, directors, crew, and marketing.
        """
        self.total_budget = self.actors_budget + self.director_budget + self.crew_budget + self.marketing_budget
        self.save()

    def __str__(self):
        return f"Budget for {self.title}"


class MovieBudgetResource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('actor', 'Actor'), ('director', 'Director'), ('crew', 'Crew')])
    salary = models.DecimalField(max_digits=15, decimal_places=2)
    contribution = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     # Calculate the contribution for the user based on their salary and role
    #     if self.role == 'actor':
    #         self.contribution = self.salary
    #         movie_budget = self.budget
    #         movie_budget.actors_budget += self.salary
    #     elif self.role == 'director':
    #         self.contribution = self.salary
    #         movie_budget = self.budget
    #         movie_budget.director_budget += self.salary
    #     elif self.role == 'crew':
    #         self.contribution = self.salary
    #         movie_budget = self.budget
    #         movie_budget.crew_budget += self.salary
    #
    #     # Recalculate the budget after adding the contribution
    #     # movie_budget.calculate_budget()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"

