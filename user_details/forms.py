from django import forms
from apps.hospital.models import Hospital

class ManagerUserForm(forms.Form):
    mobile = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=255, required=False)
    mobile = forms.CharField(max_length=15, required=False)

class FrontDeskUserForm(forms.Form):
    mobile = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    full_name = forms.CharField(max_length=255, required=True)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True)
