from django import forms

class ManagerUserForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    mobile = forms.CharField(required=False)
    full_name = forms.CharField(max_length=255, required=False)
    mobile = forms.CharField(max_length=15, required=False)
