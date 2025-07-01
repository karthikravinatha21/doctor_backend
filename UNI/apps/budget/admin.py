from django.contrib import admin
from .models import Budget, MovieBudgetResource


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'movie', 'production_house',
        'total_budget', 'actors_budget', 'director_budget',
        'crew_budget', 'marketing_budget',
        'is_collaborated', 'is_active', 'created_at'
    )
    list_filter = ('is_collaborated', 'is_active', 'production_house')
    search_fields = ('title', 'movie__title', 'production_house__name')
    # autocomplete_fields = ('movie', 'production_house')
    ordering = ('-created_at',)


@admin.register(MovieBudgetResource)
class MovieBudgetResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movie_budget', 'role', 'salary', 'contribution', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email', 'movie_budget__title')
    # autocomplete_fields = ('user', 'movie_budget')
    ordering = ('-id',)