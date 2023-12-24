from django.contrib import admin

from .models import Users , Address

class AddressAdmin(admin.ModelAdmin):
    list_display = ("id","city","state","country","code")  

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("password","passwordReSetId","slug", "otp")
    list_display = ("_id","firstName","middleName","lastName","DOB","address","logo","createdAt","updatedAt","password","passwordReSetId","email","otp","phoneNumber","address","currentActiveOrganization","slug",) 
    list_display_links = ("_id", "firstName", "middleName", "lastName")  
    list_filter = ("_id","firstName","middleName","lastName","DOB","createdAt","updatedAt","email","phoneNumber")

# Register your models here.
admin.site.register(Users , UserAdmin)
admin.site.register(Address , AddressAdmin)