from django import forms
from django.core.exceptions import ValidationError

class createOrganizationForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length = 200,
        min_length = 3,
        required=True,        
        help_text="Name",
        error_messages={
            "required" :"Organization Name is required",
            "max_length" :"Organization Name is to large",
            "min_length" :"Organization Name is too small"
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
    webSiteLink = forms.CharField(
        label="Web Site Link",
        required=False,
        error_messages={
        }
    )
    socialMediaLink = forms.CharField(
        required=False,
        label="Social Media Link",
        error_messages={
        }
    )
    contactEmail = forms.EmailField(
        label="Contact Email",
        max_length = 200,
        error_messages={
            "required" :"Email is required",
            "max_length" :"Email is to large"
        }
    )
    logo = forms.FileField(
        label="Company Logo",
        required=True,
        error_messages={
            "required" :"Logo is required",
        }
    )
    ownersDetails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),  # Adjust 'rows' as needed
        label="Owners email separated by ",
        required=False,
        error_messages={
            "required": "Owners email is required",
        },
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),  # Adjust 'rows' as needed
        label="Description",
        required=False,
        error_messages={
            "required": "Description is required",
        },
    )
    

class createTeamForm(forms.Form):
    Name = forms.CharField(
        label="Name",
        max_length = 200,
        min_length = 3,
        required=True,   
        error_messages={
            "required" :"Team Name is required",
            "max_length" :"Team Name is to large",
            "min_length" :"Team Name is too small"
        }
    )
    checkInTime = forms.TimeField(   
        label='Check In Time',
        input_formats=['%I:%M %p'],  # Specify input format if needed
        widget=forms.TimeInput(attrs={'placeholder': 'HH:MM AM/PM'}),
        required=True,
        error_messages={
            "required" :"Check In Time is required",
        }
    )
    checkOutTime = forms.TimeField(
        label="Check Out Time",
        input_formats=['%I:%M %p'],  # Specify input format if needed
        widget=forms.TimeInput(attrs={'placeholder': 'HH:MM AM/PM'}),
        required=True,   
        error_messages={
            "required" :"Check Out Time is required",
        }
    )
    Leader = forms.CharField(
        label="Leader",
        max_length = 200,
        min_length = 3,
        required=True,   
        error_messages={
            "required" :"Leader is required",
            "max_length" :"Leader is to large",
            "min_length" :"Leader is too small"
        }
    )
    Co_Leader = forms.CharField(
        label="Co-Leader's Id with','wpqeme",
        max_length = 200,
        min_length = 3,
        required=True,   
        error_messages={
            "required" :"Co-Leader is required",
            "max_length" :"Co-Leader is to large",
            "min_length" :"Co-Leader is too small"
        }
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),  # Adjust 'rows' as needed
        label="Description",
        required=False,
        error_messages={
            "required": "Description is required",
        },
    )