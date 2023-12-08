from django import forms
from django.core.exceptions import ValidationError

from Organization.models import Job_title

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
    name = forms.CharField(
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
    leader = forms.CharField(
        label="Leader",
        max_length = 200,
        min_length = 3,
        required=False,   
        error_messages={
            "required" :"Leader is required",
            "max_length" :"Leader is to large",
            "min_length" :"Leader is too small"
        }
    )
    co_Leader = forms.CharField(
        label="Co-Leader's email separated with ','",
        required=False,
        error_messages={
            "required" :"Co-Leader is required",
            "max_length" :"Co-Leader is to large",
            "min_length" :"Co-Leader is too small"
        }
    )
    team_members = forms.CharField(
        label="team members email separated with ','",
        required=False,
        error_messages={
            "required" :"Co-Leader is required",
            "max_length" :"Co-Leader is to large",
            "min_length" :"Co-Leader is too small"
        }
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), 
        label="Description",
        required=False,
        error_messages={
            "required": "Description is required",
        },
    )

    
class addEmployeeForm(forms.Form):
    email = forms.EmailField(
        label="email",
        required=True,   
        error_messages={
            "required" :"Email is required",
        }
    )

    def __init__(self, *args, organization, **kwargs):
        super(addEmployeeForm, self).__init__(*args, **kwargs)

        # Query the job titles for the specific organization
        job_titles = Job_title.objects.filter(Organization=organization)
        print(job_titles)
        
        self.fields['role'] = forms.ModelChoiceField(
            queryset=job_titles,
            label="Role",
            required=True,
            empty_label="Select a role",
            error_messages={
                "required": "Role is required",
            }
        )
    
class editEmployeeForm(forms.Form):
    email = forms.EmailField(
        label="email",
        required=True,   
        error_messages={
            "required" :"Email is required",
        },
    widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    def __init__(self, *args, organization, **kwargs):
        super(editEmployeeForm, self).__init__(*args, **kwargs)

        # Query the job titles for the specific organization
        job_titles = Job_title.objects.filter(Organization=organization)
        print(job_titles)
        
        self.fields['role'] = forms.ModelChoiceField(
            queryset=job_titles,
            label="Role",
            required=True,
            empty_label="Select a role",
            error_messages={
                "required": "Role is required",
            }
        )
    

class ChangeEmployeeRoleInTeam(forms.Form):
    Name = forms.CharField(
        label="Name",
        required=True,   
        error_messages={
            "required" :"Name is required",
        },
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    Position = forms.ChoiceField(
            choices= (("LEADER" , "LEADER") , ("CO-LEADER" , "CO-LEADER") , ("MEMBER" , "MEMBER")),
            label="Position",
            required=True,
            # empty_label="Select a role",
            error_messages={
                "required": "Position is required",
            }
        )

    def __init__(self, *args, organization, **kwargs):
        super(ChangeEmployeeRoleInTeam, self).__init__(*args, **kwargs)
        print("---------------------------------------------------------------------")

        job_titles = Job_title.objects.filter(Organization=organization)
        print(job_titles)
        choices = [(job.title, job.title) for job in job_titles]
        print(choices)
        
        self.fields['role'] = forms.ChoiceField(
            choices=choices,
            label="Role",
            required=True,
            error_messages={
                "required": "Role is required",
            }
        )
    
class addEmployeeToTeam(forms.Form):
    email = forms.CharField(
        label="Email",
        required=True,   
        error_messages={
            "required" :"Email of employee is required",
        },
        # widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    Position = forms.ChoiceField(
            choices= (("LEADER" , "LEADER") , ("CO-LEADER" , "CO-LEADER") , ("MEMBER" , "MEMBER")),
            label="Position",
            required=True,
            # empty_label="Select a role",
            error_messages={
                "required": "Position is required",
            }
        )    


class addJobTitleForm(forms.Form):
    title = forms.CharField(
        label="title",
        max_length=200,
        required=True,   
        error_messages={
            "required" :"Title is required",
            "max_length" : "Title is too long"
        }
    )