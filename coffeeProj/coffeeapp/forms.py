from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CreateCustomer(UserCreationForm): ##Register form
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
