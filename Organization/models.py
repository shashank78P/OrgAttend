import os
import uuid
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from Users.models import Address, Users
from django.utils import timezone

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

    def save(self, *args, **kwargs):
        now = timezone.now()
        ist = timezone.pytz.timezone('Asia/Kolkata')
        self.createdAt = now.astimezone(ist) if self.createdAt is None else self.createdAt.astimezone(ist)
        self.updatedAt = now.astimezone(ist)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.OrganizationId.name} ({self.userId.email})"
    
class Team(models.Model):
        name = models.CharField(max_length=100)
        checkInTime = models.TimeField()
        OrganizationId =models.ForeignKey(Organization, db_index=True , on_delete=models.CASCADE, null=True)
        checkOutTime = models.TimeField()
        description = models.CharField(
             max_length=2000,
             error_messages={
                  'invalid': 'Description is too long...'
            },
        )
        createdBy = models.ForeignKey(Users, db_index=True , on_delete=models.SET_NULL, null=True)
        createdAt = models.DateTimeField(auto_now_add=True)
        updatedAt = models.DateTimeField(auto_now=True)
        
        def __str__(self):
           return f"{self.name} ({self.checkInTime} - {self.checkOutTime})"


def isRole(value):
    if value in ["LEADER" , "CO-LEADER","MEMBER"]:
        return value
    else:
        raise ValidationError("invalid employee role")


class TeamMember(models.Model):
        role = models.CharField(
             max_length=10 ,
             db_index=True,
             validators=[
                  isRole
             ]
        )
        TeamId =models.ForeignKey(Team, db_index=True , on_delete=models.CASCADE, null=True)
        OrganizationId =models.ForeignKey(Organization, db_index=True , on_delete=models.CASCADE, null=True)
        userId = models.ForeignKey(Users , db_index=True , on_delete=models.CASCADE, null=True , related_name="user")
        # addedBy = models.ForeignKey(Users, db_index=True , on_delete=models.SET_NULL, null=True)
        createdBy = models.ForeignKey(Users, db_index=True , on_delete=models.SET_NULL, null=True , related_name="createdBy")
        createdAt = models.DateTimeField(auto_now_add=True)
        updatedAt = models.DateTimeField(auto_now=True)

        # def save(self, *args, **kwargs):
        #     now = timezone.now()
        #     ist = timezone.pytz.timezone('Asia/Kolkata')
        #     # self.createdAt = now.astimezone(ist) if self.createdAt is None else self.createdAt.astimezone(ist)
        #     # self.updatedAt = now.astimezone(ist)

        #     super().save(*args, **kwargs)

        def __str__(self):
           return f"{self.role} | {self.OrganizationId.name} | ({self.userId.firstName} {self.userId.lastName})"
        
class Job_title(models.Model):
    title = models.CharField(
        unique=True,
        max_length=100,
        error_messages={
            "unique": "Tile is already exist",
            'invalid': 'Please enter a valid job title name.',
            'max_length': 'Job title name must be smaller than 100 characters.',
            # 'min_length': 'Job title name must have minimum of 3 characters.',
        },
    )
    createdBy = models.ForeignKey(Users , on_delete=models.CASCADE , null=True)
    Organization = models.ForeignKey(Organization , db_index=True , on_delete=models.SET_NULL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True , null=True)

    def __str__(self):
        return f"{self.title} ({self.Organization.name})"

class Employee(models.Model):
    _id = models.AutoField(auto_created=True, primary_key=True)
    employee = models.ForeignKey(Users , on_delete=models.CASCADE , related_name='employee')
    Organization = models.ForeignKey(Organization , db_index=True , on_delete=models.CASCADE, null=True)
    jobTitle = models.ForeignKey(Job_title , db_index=True , on_delete=models.CASCADE, null=True)
    createdBy = models.ForeignKey(Users , on_delete=models.CASCADE , related_name='created_employee' , null=True)
    createdAt = models.DateTimeField(auto_now_add=True , null=True)
    updatedAt = models.DateTimeField(auto_now=True , null=True)

    def __str__(self):
        return f"{self.employee.firstName} {self.employee.lastName}"


class LeaveRequest(models.Model):
    leaveType = models.CharField(max_length=50 , null=True)
    status = models.CharField(max_length=50 , null=True , default="Pending")
    fromDate = models.DateField(max_length=50 , null=True)
    toDate = models.DateField(null=True)
    reason = models.CharField(max_length=10000 , null=True)
    TeamId = models.ForeignKey(Team , db_index=True , on_delete=models.CASCADE, null=True)
    Organization = models.ForeignKey(Organization , db_index=True , on_delete=models.CASCADE, null=True)
    createdBy = models.ForeignKey(Users , on_delete=models.CASCADE , null=True , related_name="leaveRequestCreatedBy")
    verifiedBy = models.ForeignKey(Users , on_delete=models.CASCADE , null=True , related_name="verifiedBy")
    createdAt = models.DateTimeField(auto_now_add=True , null=True)
    updatedAt = models.DateTimeField(auto_now=True , null=True)

    def __str__(self):
        return f"{self.createdBy.firstName} {self.createdBy.middleName} {self.createdBy.lastName} ({self.fromDate}-{self.toDate}) ({self.leaveType})"

class Attendance(models.Model):
    note = models.CharField(max_length=10000 , null=True)
    attendance = models.BooleanField(default=False)
    TeamId = models.ForeignKey(Team , db_index=True , on_delete=models.CASCADE, null=True)
    Organization = models.ForeignKey(Organization , db_index=True , on_delete=models.CASCADE, null=True)
    createdBy = models.ForeignKey(Users , on_delete=models.CASCADE , null=True , related_name="attendanceTaken")
    userId = models.ForeignKey(Users , on_delete=models.CASCADE , null=True , related_name="user_employee")
    takenAt = models.DateField(null=True)
    createdAt = models.DateTimeField(auto_now_add=True , null=True)
    updatedAt = models.DateTimeField(auto_now=True , null=True)

    def __str__(self):
        return f"{self.userId.firstName} {self.userId.middleName} {self.userId.lastName} ({self.createdAt}) ({self.attendance})"


# tm.objects.filter(OrganizationId = o , TeamId_id__in = teamDetails) 
#>>> teamMem = t.objects.annotate(count = Count('teammember'))                          

# def runQuery(query):
    # cursor = connection.cursor()
    # cursor.execute(query)
    # return cursor.fetchall()
# 
# from django.db import connection                                                                                 
# runQuery("select * from Users_users") 