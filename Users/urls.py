from django.urls import path
from . import views

urlpatterns = [
    path("sign-up" , views.signUp),
    path("log-in" , views.login),
    path("add" , views.add),
    path("edit/<slug:slug>" , views.edit ),
    path("<slug:slug>" , views.index , name="user-profile"),
]