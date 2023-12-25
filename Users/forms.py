from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from Organization.models import Team , TeamMember

class UserProfileEdit(forms.Form):
    logo = forms.forms.FileField(
        label="User Profile Pic",
        required=False,
        error_messages={
            "required" :"Logo is required",
        }
    )

    # email = forms.EmailField(
    #     label="Email",
    #     max_length = 200,
    #     error_messages={
    #         "required" :"Email is required",
    #         "max_length" :"Email is to large"
    #     }
    # )
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

    DOB = forms.DateField(
        label="Date Of Birth",
        widget=forms.DateInput(attrs={'type': 'date' , 'max' : date.today().strftime('%Y-%m-%d')} ),
        error_messages={
            "required" :"DOB is required"
        }
    )

    phoneNumber = forms.CharField(
        label="Phone Number",
        max_length = 10,
        min_length=10,
        error_messages={
            "required" :"Phone Number is required",
            "max_length" :"Phone Number is to large",
            "min_length" :"Phone Number is too small"
        }
    )
    city = forms.CharField(
        label="City",
        required=True,
        max_length = 50,
        min_length=3,
        error_messages={
            "max_length" :"City name is too large",
            "min_length" :"City name is too small"
        }
    )
    state = forms.CharField(
        label="State",
        required=True,
        max_length = 500,
        min_length=3,
        error_messages={
            "max_length" :"State name is too large",
            "min_length" :"State name is too small"
        }
    )
    country = forms.CharField(
        label="Country",
        required=True,
        max_length = 500,
        min_length=3,
        error_messages={
            "max_length" :"Country name is too large",
            "min_length" :"Country name is too small"
        }
    )
    code = forms.CharField(
        label="Pin Code",
        required=True,
        max_length = 500,
        min_length=3,
        error_messages={
            "max_length" :"Pin Code is too large",
            "min_length" :"Pin Code is too small"
        }
    )

class signUpForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )

class changePasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )
    otp = forms.CharField(
        label="OTP",
        max_length = 4,
        error_messages={
            "required" :"OTP is required"
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

class signUpForm2(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )
    otp = forms.CharField(
        label="OTP",
        max_length = 4,
        error_messages={
            "required" :"OTP is required"
        }
    )
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

    def __init__(self, *args, organization , user, **kwargs):
        super(LeaveRequestForm, self).__init__(*args, **kwargs)

        # Query the job titles for the specific organization
        teamMem = TeamMember.objects.filter(OrganizationId=organization ,userId = user)

        team = Team.objects.filter(id__in=teamMem.values_list('TeamId', flat=True))

        print(team)
        
        self.fields['team'] = forms.ModelChoiceField(
            queryset=team,
            label="Team",
            required=True,
            empty_label="Select a Team",
            error_messages={
                "required": "Team is required",
            }
        )

        new_fields = {
            'LeaveType': self.fields['LeaveType'],
            'From': self.fields['From'],
            'To': self.fields['To'],
            'team': forms.ModelChoiceField(
                queryset=team,
                label="Team",
                required=True,
                empty_label="Select a Team",
                error_messages={
                    "required": "Team is required",
                }
            ),
            'reason': self.fields['reason'],
        }

        self.fields = new_fields
