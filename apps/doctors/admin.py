from django.contrib import admin
from .models import Doctor, Specialisation, Hospital
from django.utils.translation import gettext_lazy as _

class DoctorAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'id', 'code', 'name', 'is_online_appointment_enable', 'is_logged_in', 'start_date', 'end_date'
    )

    # Search fields to make it searchable in the admin panel
    search_fields = ('code', 'name', 'hospital__description', 'speciality__code',)

    # Add filters for some fields like hospital, is_logged_in
    list_filter = ('is_logged_in', 'hospital', 'is_online_appointment_enable', 'speciality')

    # Fields to display in the form view when adding/editing a doctor
    fields = (
        'code', 'name', 'speciality', 'hospital', 'designation', 'title_text', 'qualification',
        'educational_degrees', 'photo', 'content', 'notes', 'fellowship_membership', 'field_expertise',
        'languages_spoken', 'awards_achievements', 'talks_publications', 'experience', 'display_order',
        'allow_website','is_online_appointment_enable', 'slug',
    )

    # Use filter_horizontal to improve the UI for ManyToMany relationships (like Specialisation)
    filter_horizontal = ('speciality', 'hospital')

    # Custom method to show the specializations as a string
    def speciality_display(self, obj):
        return ", ".join([s.code for s in obj.speciality.all()])
    speciality_display.short_description = _("Specialities")

    def hospital_display(self, obj):
        return ", ".join([s.code for s in obj.hospital.all()])
    speciality_display.short_description = _("Hospital")

    # Making sure the `code` field is unique and readonly
    # readonly_fields = ('code',)

    # Customizing the __str__ representation of the doctor (for admin list)
    def __str__(self, obj):
        return f'{obj.name} ({obj.code})'

    # Adding custom actions (example: toggle is_logged_in status)
    def toggle_is_logged_in(self, request, queryset):
        for doctor in queryset:
            doctor.is_logged_in = not doctor.is_logged_in
            doctor.save()
    toggle_is_logged_in.short_description = _("Toggle is_logged_in status")

    actions = ['toggle_is_logged_in']

# Register the DoctorAdmin class with the Doctor model
admin.site.register(Doctor, DoctorAdmin)
