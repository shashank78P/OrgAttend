import uuid
from django.db import models
from django.core.validators import EmailValidator
from django.utils.text import slugify
from Users.models import Address, Users

# Create your models here.
class Organization(models.Model):
    _id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(
        unique=True,
        max_length=100,
        error_messages={
            "unique": "Organization name is already exist",
            'invalid': 'Please enter a valid organization name.'
        },
        db_index=True,
    )
    address = models.ForeignKey(Address , on_delete=models.SET_NULL, null=True)
    webSiteLink = models.CharField(max_length=2000)
    socialMediaLink = models.CharField(max_length=2000)
    contactEmail = models.EmailField(
        unique=True,
        error_messages={
            "unique": "This email is already exist",
            'invalid': 'Please enter a valid email address.'
        },
        validators=[EmailValidator()],
        db_index=True
    )
    logo = models.ImageField(
        upload_to="organizationLogo",
        default="organization.png",
        max_length=20000 , 
        error_messages={
            'invalid': 'Invalid file (file is not acceptable).'
        },
    )
    description = models.CharField(max_length=2000)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="" , null=False , blank=True , db_index=True )

    def save(self , *args , **kwargs):
        slug = f"{self.name} {uuid.uuid4() }"
        print(slug)
        self.slug = slugify(slug)
        super().save(*args , **kwargs)

    def __str__(self):
        return f"{self.name}"


class OwnerDetails(models.Model):
    OrganizationId =models.ForeignKey(Organization , on_delete=models.CASCADE, null=True)
    userId = models.ForeignKey(Users , on_delete=models.CASCADE, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.OrganizationId.name} ({self.userId.email})"