from .models import UserInfo
from django.contrib.auth.models import User
from django import forms

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['school','company','profession','address','aboutme']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']