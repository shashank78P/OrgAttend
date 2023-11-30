from django.urls import path
from . import views

urlpatterns = [
    path("create-organization" , views.createOrganization),
    path("create-team" , views.createTeam),
    path("<slug:slug>" , views.createTeam),
]