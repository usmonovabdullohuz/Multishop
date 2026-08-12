from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"Password"
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"Re-Password"
    }))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'phone']
        widgets = {
            "username":forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Username"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number"
            })
        }


class SignInForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class":"form-control",
        "placeholder":"Username"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"*****"
    }))


