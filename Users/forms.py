from django import forms
from django.core.exceptions import ValidationError

class signUpForm(forms.Form):
    firstName = forms.CharField(
        label="First Name",
        max_length = 200,
        error_messages={
            "required" :"First Name is required",
            "max_length" :"First Name is to large",
            "min_length" :"First Name is too small"
        }
    )
    middleName = forms.CharField(
        label="Middle Name",
        required=False,
        max_length = 20,
        min_length=1,
        error_messages={
            "max_length" :"Middle Name is too large",
            "min_length" :"Middle Name is too small"
        }
    )
    lastName = forms.CharField(
        label="Last Name",
        required=False,
        max_length = 20,
        min_length=1,
        error_messages={
            "max_length" :"Last Name is to large",
            "min_length" :"Last Name is too small"
        }
    )
    email = forms.EmailField(
        label="Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        max_length=200,
        min_length=8,
        error_messages={
            "required" :"Password is required",
            "max_length" :"Password is to large",
            "min_length" :"Password must have atleast 8 character"
        }
    )
    confirmPassword = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        max_length=200,
        min_length=8,
        error_messages={
            "required" :"Confirm Password is required",
            "max_length" :"Confirm Password is to large",
            "min_length" :"Confirm Password must have atleast 8 character"
        }
    )

class logInForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        max_length=200,
        min_length=8,
        error_messages={
            "required" :"Password is required",
            "max_length" :"Password is to large",
            "min_length" :"Password must have atleast 8 character"
        }
    )