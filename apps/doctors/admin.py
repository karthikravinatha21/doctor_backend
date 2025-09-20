import csv
import datetime
import random
import re
from io import TextIOWrapper
from django.utils.html import format_html
import numpy as np
import pandas as pd
from django.contrib import admin, messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render
from django.urls import path

from .models import Doctor, Specialisation, Hospital
from django.utils.translation import gettext_lazy as _

from django import forms

class DoctorUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")

class DoctorAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'id', 'username', 'code', 'full_name', 'profile_image_tag', 'is_online_appointment_enable', 'is_logged_in', 'start_date', 'end_date'
    )

    # Search fields to make it searchable in the admin panel
    search_fields = ('username', 'code', 'full_name', 'speciality__code',)

    # Add filters for some fields like hospital, is_logged_in
    list_filter = ('is_logged_in', 'hospital', 'is_online_appointment_enable', 'speciality')

    # Fields to display in the form view when adding/editing a doctor
    fields = (
        'username', 'code', 'full_name', 'email', 'password', 'speciality', 'hospital', 'designation', 'title_text', 'qualification',
        'educational_degrees', 'profile_image_preview', 'photo', 'content', 'notes', 'fellowship_membership', 'field_expertise',
        'languages_spoken', 'awards_achievements', 'talks_publications', 'experience', 'meta_title',
        'meta_description', 'meta_keywords', 'other_meta_tags', 'display_order', 'allow_website',
        'is_online_appointment_enable', 'slug', 'hv_consultation_charges', 'vc_consultation_charges',
        'pr_consultation_charges', 'start_date', 'end_date', 'is_primary_consultation_doctor',
    )
    readonly_fields = ('username', 'profile_image_preview',)

    def profile_image_tag(self, obj):
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="50" height="50" style="object-fit:cover; border-radius:50%;" />'
                '</a>',
                obj.photo.url
            )
        return "-"
    profile_image_tag.short_description = "Photo"

    def profile_image_preview(self, obj):
        if obj.photo and hasattr(obj.photo, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="150" height="150" style="object-fit:cover; border-radius:8px;" />'
                '</a>',
                obj.photo.url
            )
        return "No image uploaded"
    profile_image_preview.short_description = "Photo Preview"

    # Use filter_horizontal to improve the UI for ManyToMany relationships (like Specialisation)
    filter_horizontal = ('speciality', 'hospital')

    change_list_template = "admin/doctor_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-doctors/', self.admin_site.admin_view(self.upload_doctors), name="upload-doctors"),
        ]
        return custom_urls + urls

    def upload_doctors(self, request):
        if request.method == "POST":
            form = DoctorUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                if csv_file.name.endswith('.csv'):
                    df = pd.read_csv(csv_file)
                elif csv_file.name.endswith('.xlsx'):
                    df = pd.read_excel(csv_file)
                else:
                    raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")
                # data = csv_file.file
                # reader = csv.DictReader(data)
                created_count = 0
                updated_count = 0
                df = df.replace({np.nan: None})  # First replace actual NaNs
                df = df.applymap(lambda x: None if (x is None or (isinstance(x, str) and x.strip() == '')) else x)

                def clean_hospital_name(value):
                    if value:
                        return re.sub(r'\s*\([^)]*\)$', '', value).strip()
                for _, row in df.iterrows():
                    hospital_name = clean_hospital_name(row['Hospital Ids'])
                    if hospital_name:
                        hospital_qs = Hospital.objects.filter(hospital_name=hospital_name)
                        defaults = {
                            'full_name': row['First Name'],
                            'designation': row['Designation'],
                            'qualification': row['Qualification'],
                            'educational_degrees': row['Educational degrees'],
                            'fellowship_membership': row['Fellowship membership'],
                            'field_expertise': row['Field expertise'],
                            'languages_spoken': row['Languages spoken'],
                            'awards_achievements': row['Awards achievements'],
                            'talks_publications': row['Talks publications'],
                            'experience': row['Experience'],
                            'is_online_appointment_enable': True,
                            'start_date': datetime.datetime.now(),
                            'code': f'D-04d{random.randint(0, 9999)}'
                        }

                        doctor, created = Doctor.objects.update_or_create(
                            # code=row['code'],
                            full_name= row['First Name'],
                            defaults=defaults
                        )
                        doctor.hospital.set(hospital_qs)
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                messages.success(request,
                                 f"Doctors uploaded successfully: {created_count} created, {updated_count} updated.")
                return redirect("..")
        else:
            form = DoctorUploadForm()

        return render(request, "admin/upload_doctors.html", {"form": form})

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            raw_password = form.cleaned_data['password']
            obj.password = make_password(raw_password)
        super().save_model(request, obj, form, change)

    # Custom method to show the specializations as a string
    def speciality_display(self, obj):
        return ", ".join([s.code for s in obj.speciality.all()])

    speciality_display.short_description = _("Specialities")

    def hospital_display(self, obj):
        return ", ".join([s.code for s in obj.hospital.all()])

    hospital_display.short_description = _("Hospital")

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
