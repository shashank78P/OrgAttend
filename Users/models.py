from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

# creating a validator function
def isPhoneNumber(value):
    if len(value) == 10:
        return value
    else:
        raise ValidationError("Phone number must have only 10 digit")
    
def isValidDate(value):
    today = date.today()
    if(today.year == value.year and today.month == value.month and today.day == value.day):
        raise ValidationError("Invalid date")
    else:
        return value

# users class inheriting models.Model
class Users(models.Model):
    id = models.AutoField(auto_created=True , primary_key=True)
    FirstName = models.CharField(max_length=50)
    MiddleName = models.CharField(max_length=20)
    LastName = models.CharField(max_length=20)
    phoneNumber = models.CharField(max_length=10 , 
                unique = True,
                null=False,
                blank=False,
                default='0',
                error_messages ={
                "unique":"User with this number is already exist",
                "max_length":"Phone number must have only 10 digit",
                },
                validators =[isPhoneNumber]
            )
    email :  models.EmailField( 
                unique = True,
                error_messages ={
                "unique":"User with this number is already exist",
                'invalid': 'Please enter a valid email address.'
                },
            )
    DOB : models.DateField(
        validators =[isValidDate]
    )
    createdAt : models.DateTimeField(
        default=date.today()
    )
    updatedAt : models.DateTimeField(
        default=date.today()
    )

    
