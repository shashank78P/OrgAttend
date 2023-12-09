from datetime import date
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
    
class LeaveRequestForm(forms.Form):
    LeaveType = forms.ChoiceField(
            choices= (
                ("Privilege Leave","Privilege Leave"),
                ("Casual Leave","Casual Leave"),
                ("Sick Leave","Sick Leave"),
                ("Maternity Leave","Maternity Leave"),
            ),
            label="LeaveType",
            required=True,
            error_messages={
                "required": "Leave type is required",
            }
    )
    From = forms.DateField(
        label="From",
        widget=forms.DateInput(attrs={'type': 'date' , 'min' : date.today().strftime('%Y-%m-%d')} ),
        error_messages={
            "required" :"From Date is required",
        }
    )
    To = forms.DateField(
        label="To",
        widget=forms.DateInput(attrs={'type': 'date'} ),
        error_messages={
            "required" :"To Date is required",
        }
    )
    reason = forms.CharField(
        label="Reason",
        widget=forms.Textarea(attrs={'placeholder': 'Reason for leave'} ),
        max_length=10000,
        min_length=3,
        error_messages={
            "required" :"reason is required",
            "max_length" :"reason is too large",
            "min_length" :"reason must have atleast 3 character"
        }
    )
