from django.shortcuts import render
from django.http import HttpResponse ,HttpResponseServerError , HttpResponseRedirect

# Create your views here.

def index(request , slug):
    try:
        return render(request ,"Profile.html" , { 'slug' : slug })
    except():
        HttpResponseServerError("Internal Server error")


def signUp(request) :
    try:
        print("printing data")
        print(request.method)
        if(request.method == "POST"):
            data = request.POST
            print("printing data")
            print(data)
            return HttpResponseRedirect("/users/log-in")

        elif(request.method == "GET"):
            return render(request ,"SignUp.html")
    except():
        HttpResponseServerError("Internal Server error")

def login(request) :
    try:
        return render(request ,"LogIn.html")
    except():
        HttpResponseServerError("Internal Server error")

def add(request) :
    try:
        return render(request ,"SignUp.html")
    except():
        HttpResponseServerError("Internal Server error")

def edit(request , slug) :
    try:
        return render(request ,"Edit.html" , { 'slug' : slug })
    except():
        HttpResponseServerError("Internal Server error")

def delete(request , slug) :
    try:
        return render(request ,"delete.html" , { 'slug' : slug })
    except():
        HttpResponseServerError("Internal Server error")