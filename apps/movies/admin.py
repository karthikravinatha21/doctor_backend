from django.contrib import admin
from .models import (
    Movie, ActorPortfolio, ActorPayment, PaymentTypeRate,
    ActorAudition, ActorAward
)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_date', 'genre', 'language', 'duration_minutes', 'production_house', 'total_budget', 'box_office_collection', 'is_active')
    list_filter = ('genre', 'language', 'is_active', 'production_house')
    # search_fields = ('title', 'genre', 'language')
    ordering = ('-release_date',)
    # autocomplete_fields = ('production_house',)


@admin.register(ActorPortfolio)
class ActorPortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'portfolio_url')
    # search_fields = ('actor__first_name', 'actor__last_name', 'actor__email')
    # autocomplete_fields = ('actor',)


class PaymentTypeRateInline(admin.TabularInline):
    model = PaymentTypeRate
    extra = 1


@admin.register(ActorPayment)
class ActorPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'upi_id', 'interested_in_internship')
    list_filter = ('interested_in_internship',)
    # search_fields = ('actor__first_name', 'actor__last_name', 'actor__email')
    # autocomplete_fields = ('actor',)
    filter_horizontal = ('shooting_roles',)
    inlines = [PaymentTypeRateInline]


@admin.register(ActorAudition)
class ActorAuditionAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'movie', 'role', 'audition_date', 'outcome')
    list_filter = ('outcome', 'audition_date')
    # search_fields = ('actor__first_name', 'movie__title', 'role')
    # autocomplete_fields = ('actor', 'movie')


@admin.register(ActorAward)
class ActorAwardAdmin(admin.ModelAdmin):
    list_display = ('id', 'actor', 'award_name', 'year', 'category', 'nomination_status')
    list_filter = ('year', 'nomination_status')
    # search_fields = ('actor__first_name', 'award_name', 'category')
    # autocomplete_fields = ('actor',)
