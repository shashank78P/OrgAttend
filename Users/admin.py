from django.contrib import admin

from .models import Users , Address

class AddressAdmin(admin.ModelAdmin):
    list_display = ("id","city","state","country","code")  

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("password","passwordReSetId","slug")
    list_display = ("_id","firstName","middleName","lastName","DOB","address","createdAt","updatedAt","password","passwordReSetId","email","phoneNumber","slug",) 
    list_display_links = ("_id", "firstName", "middleName", "lastName")  # Make '_id' clickable
    list_filter = ("_id","firstName","middleName","lastName","DOB","createdAt","updatedAt","email","phoneNumber")

# Register your models here.
admin.site.register(Users , UserAdmin)
admin.site.register(Address , AddressAdmin)