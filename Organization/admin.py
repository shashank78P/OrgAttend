from django.contrib import admin

from .models import OwnerDetails, Organization

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

# Register your models here.
admin.site.register(Organization , OrganizationAdmin)
admin.site.register(OwnerDetails , OwnerDetailsAdmin)