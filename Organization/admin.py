from django.contrib import admin

from .models import OwnerDetails, Organization , Team , TeamMember , Employee ,Job_title

class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "_id","name","address","webSiteLink","socialMediaLink","contactEmail","logo","description","createdAt","updatedAt", "slug",
    ) 
    list_display_links = ("_id", "name",)  # Make '_id' clickable
    list_filter = ("_id","name","createdAt","updatedAt")

class OwnerDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "OrganizationId" , "userId","createdAt","updatedAt",
    ) 
    list_filter = ("createdAt","updatedAt")

class TeamsAdmin(admin.ModelAdmin):
    list_display = (
        "name","checkInTime","OrganizationId","checkOutTime","description","createdBy","createdAt","updatedAt",
    ) 
    list_filter = ("name","id","OrganizationId","createdAt","updatedAt")

class TeamMembersAdmin(admin.ModelAdmin):
    list_display = ("id","role","TeamId","OrganizationId","userId","createdAt","createdBy","updatedAt") 
    list_filter = ("role","TeamId","OrganizationId","userId","createdAt","updatedAt")

class JobTitleAdmin(admin.ModelAdmin):
    list_display = ("title","Organization","createdAt","createdBy","updatedAt") 
    list_filter = ("createdAt","updatedAt")

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("_id","employee","Organization","jobTitle","createdAt","createdBy","updatedAt") 
    list_filter = ("createdAt","updatedAt")

# Register your models here.
admin.site.register(Organization , OrganizationAdmin)
admin.site.register(OwnerDetails , OwnerDetailsAdmin)
admin.site.register(Team , TeamsAdmin)
admin.site.register(TeamMember , TeamMembersAdmin)
admin.site.register(Employee , EmployeeAdmin)
admin.site.register(Job_title , JobTitleAdmin)