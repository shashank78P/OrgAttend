import os
from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse ,HttpResponseServerError , HttpResponseRedirect, JsonResponse ,Http404
from django.contrib import messages
from django.contrib.auth.hashers import make_password , check_password
from .forms import signUpForm , logInForm
from .models import Users 
from datetime import datetime , timedelta
import jwt
from dotenv import load_dotenv

# Create your views here.

print( datetime.utcnow() + timedelta(days= 2))

def index(request , slug):
    try:
        cookie = request.get_signed_cookie(
            'authorization',
            salt=os.environ.get('SECRET_KEY'),
        )
        print("request")
        if not request.path:
            return Http404("Page Not found")
        slug = request.path.split("/")[-1]
        print(request.path)
        token = cookie.split(" ")[1]
        decoded_data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms='HS256')
        user = Users.objects.get(slug = slug)
        return render(request ,"Profile.html" , { 'slug' : slug , 'user' : user })
    except jwt.ExpiredSignatureError:
        return render(request ,"Profile.html" , { 'slug' : slug , messages : messages.error(request, "Token has expired.")})
    except jwt.InvalidTokenError:
        return render(request ,"Profile.html" , { 'slug' : slug , messages : messages.error(request, "Invalid token.")})
    except Exception as e:
        error_message = str(e)
        return HttpResponseServerError(error_message)

def signUp(request) :
    try:
        if(request.method == "POST"):
            form = signUpForm(request.POST)
            # data = request.POST
            # print(form.cleaned_data)
            print(request.POST)
            password=request.POST["password"]
            confirmPassword=request.POST["confirmPassword"]
            print(password + " "+ confirmPassword)
            if(password != confirmPassword):
                form.add_error("confirmPassword" ,"Passwords not matched")
            if form.is_valid():
                user = Users(
                    firstName = request.POST["firstName"],
                    middleName = request.POST["middleName"],
                    lastName = request.POST["lastName"],
                    email = request.POST["email"],
                    password = make_password(request.POST["password"]),
                )
                print("user")
                print(user)
                user.save()
                return HttpResponseRedirect("/users/log-in")
            else:
                return render(request ,"SignUp.html" , { 'form' : form })

        elif(request.method == "GET"):
            form = signUpForm()
            return render(request ,"SignUp.html" , { 'form' : form })
    except():
        HttpResponseServerError("Internal Server error")

def login(request) :
    try:
        if(request.method == "POST"):
            form = logInForm(request.POST)
            print(request.POST)
            password=request.POST["password"]
            email=request.POST["email"]
            print(email , password)

            user = Users.objects.get(email = email)

            print(user)
            print(user.password)
            print(os.environ.get('SECRET_KEY'))
            print("checking password")
            print(check_password(password , user.password))
            if(check_password(password , user.password)):
                response = HttpResponseRedirect(f"/users/{user.slug}")
                render(request ,"Profile.html" , { "slug" : "" })
                token = jwt.encode( {
                    '_id' : user._id,
                    },
                    os.environ.get('SECRET_KEY'),
                    algorithm='HS256'
                 )
                print("token")
                print(token)
                response.set_signed_cookie(
                        'authorization' , f"Bearer {token}" ,
                        salt="attendance123",
                        expires= datetime.utcnow() + timedelta(days= 1) 
                    )
                return response
            else:
                form.add_error("password" ,"Invalid LogIn")
                return render(request ,"LogIn.html" , { 'form' : form })
        else:
            form = logInForm()
            return render(request ,"LogIn.html", { 'form' : form })
    except():
        form = logInForm()
        return render(request ,"LogIn.html", { 'form' : form })
        # HttpResponseServerError("Internal Server error")

def home(request , slug) :
    try:
        return render(request ,"Home.html")
    except():
        HttpResponseServerError("Internal Server error")

def attendanceHistory(request , slug) :
    try:
        return render(request ,"AttendanceHistory.html")
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

def getUserByEmail(email):
    try:
        # email = request.GET.get("email")
        user = get_object_or_404(Users , email = email)

        return JsonResponse({
            'firstName' : user[0].firstName,
            'middleName' : user[0].middleName,
            'lastName' : user[0].lastName,
            'DOB' : user[0].DOB,
            'email' : user[0].email,
            'phoneNumber' : user[0].phoneNumber,
            'address' : user[0].address,
            'error' : False
        })
    except Exception as e:
        return JsonResponse({ 'error' : True , 'message' : e})