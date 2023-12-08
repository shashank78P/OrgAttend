from django.urls import path
from . import views

urlpatterns = [
    path("create-organization" , views.createOrganization),
    path("create-team" , views.createTeam),
    path("add-employee" , views.AddEmployee),
    path("add-job-title" , views.AddJobTitle),
    path("get-all-organization-list" , views.getAllOrganizationList),
    path("leave-request/<slug:slug>" , views.leaveRequest),
    path("teams/<slug:slug>" , views.teams),
    path("teams/<slug:slug>/<id>" , views.teamMembersDetails),
    path("job-title/<slug:slug>" , views.jobTitle),
    path("job-title/<slug:slug>/<id>" , views.jobTitleDetails),
    path("employees/<slug:slug>" , views.employees),
    path("<slug:slug>" , views.companyProfile),
]