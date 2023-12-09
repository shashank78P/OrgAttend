import math
import numpy as np
import json
import os
from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse ,HttpResponseServerError , HttpResponseRedirect, JsonResponse ,Http404
from django.contrib import messages
from django.contrib.auth.hashers import make_password , check_password
from .forms import LeaveRequestForm, signUpForm , logInForm
from .models import Users 
from Organization.models import LeaveRequest, Organization
from datetime import datetime , timedelta
import jwt
from dotenv import load_dotenv
from django.db.models import Q

# Create your views here.

print( datetime.utcnow() + timedelta(days= 2))

def index(request , slug):
    try:
        # cookie = request.get_signed_cookie(
        #     'authorization',
        #     salt=os.environ.get('SECRET_KEY'),
        # )
        # print("request")
        # if not request.path:
        #     return Http404("Page Not found")
        # slug = request.path.split("/")[-1]
        # print(request.path)
        # token = cookie.split(" ")[1]
        # decoded_data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms='HS256')
        print('request.session["user"]')
        print(request.session['user'])
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
    except Exception as e:
            print(e)
            HttpResponseServerError(e)

def login(request) :
    try:
        if(request.method == "POST"):
            form = logInForm(request.POST)
            print(request.POST)
            password=request.POST["password"]
            email=request.POST["email"]

            user = Users.objects.get(email = email)

            if(check_password(password , user.password)):
                response = HttpResponseRedirect(f"/users/{user.slug}")
                render(request ,"Profile.html" , { "slug" : "" })
                token = jwt.encode( {
                    '_id' : user._id,
                    },
                    os.environ.get('SECRET_KEY'),
                    algorithm='HS256'
                 )
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
    except Exception as e:
        print(e)
        return render(request ,"LogIn.html", { 'form' : form })
        # HttpResponseServerError("Internal Server error")

def home(request , slug) :
    try:    
        user = request.session["user"]
        print(user)
        return render(request ,"Home.html" , { 'slug' : slug , "user" : user , "endpoint":"users" , "baseUrl" : os.environ.get('FRONTEND')})
    except Exception as e:
        print('Internal Server error')
        return HttpResponseServerError(e)
    
def homePage(request):
    try:
        user = request.session["user"]
        # org = Organization.objects.get(_id = user["currentActiveOrganization"])
        # slug = org.slug
        return HttpResponseRedirect(f"/users/{user["slug"]}")
    except Exception as e:
        return HttpResponseServerError(e)

def setCurrentActiveOrganization(request):
    try:
        print("called set current org.....")
        if(request.method == "POST"):
            userData = request.session["user"]
            data = json.loads(request.body.decode('utf-8'))
            user = Users.objects.get(_id = userData["_id"])

            print(user)
            org = get_object_or_404(Organization , slug = data["slug"])
            print(org)
            print(int(org._id))
            user.currentActiveOrganization =  int(org._id)
            user.save()
            return JsonResponse({ "data" : "" , "message" : "Switched sucessfully" })
        else:
            return Http404()
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def attendanceHistory(request , slug) :
    try:
        user = request.session["user"]
        return render(request ,"AttendanceHistory.html" , { 'slug' : slug , "user" : user , "endpoint":"users" , "baseUrl" : os.environ.get('FRONTEND')})
    except Exception as e:
            print(e)
            HttpResponseServerError(e)

def add(request) :
    try:
        return render(request ,"SignUp.html")
    except Exception as e:
            print(e)
            HttpResponseServerError(e)

def edit(request , slug) :
    try:
        return render(request ,"Edit.html" , { 'slug' : slug })
    except Exception as e:
            print(e)
            HttpResponseServerError(e)

def delete(request , slug) :
    try:
        return render(request ,"delete.html" , { 'slug' : slug })
    except Exception as e:
            print(e)
            HttpResponseServerError(e)

def getUserByEmail(email):
    try:
        # email = request.GET.get("email")
        # user = get_object_or_404(Users , email = email)
        user = Users.objects.get(email = email)

        return user

        # return JsonResponse({
        #     'firstName' : user.firstName,
        #     'middleName' : user.middleName,
        #     'lastName' : user.lastName,
        #     'DOB' : user.DOB,
        #     'email' : user.email,
        #     'phoneNumber' : user.phoneNumber,
        #     'address' : user.address,
        #     'error' : False
        # })
    except Exception as e:
        return JsonResponse({ 'error' : True , 'message' : e})

def formateLeaveRequest(leaveRequestData):
    try:
        tableTitle = ["name","status","leaveType","fromDate","toDate","reason"]
        tableData = []
        print(tableTitle)
        for i in  range(0,len(leaveRequestData)):
            data = leaveRequestData[i]
            print(data)

            tableData.append([ 
                f'{data.createdBy.firstName} {data.createdBy.middleName} {data.createdBy.lastName}',
                f'{data.status}',
                f'{data.leaveType}',
                f'{data.fromDate}',
                f'{data.toDate}',
                f'{data.reason}',
                f'{data.id}',
            ])
        return tableTitle , tableData
    except Exception as e:
        return HttpResponseServerError(e)

def leaveRequest(request , slug): 
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])
        org = get_object_or_404( Organization, _id = currentUser["currentActiveOrganization"])
        print("leaveRequest")
        search=""
        rows=10
        page=0
        data = request.POST
        print(data)


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"])
        

        print(search , rows)

        skip = page*rows
        print(userData)
        print(org)

        leaveReq = LeaveRequest.objects.filter(Q(createdBy = userData) & Q(Organization = org) &
         (
        Q(status__icontains=search) |
        Q(reason__icontains=search) |
        Q(leaveType__icontains=search) |
        Q(fromDate__icontains=search) |
        Q(toDate__icontains=search) 
        )).order_by("-createdAt")
        
        openAction = True
        editAction = False
        deleteAction = True

        print("leaveReq===>")
        print(leaveReq)

        tableTitle , tableData  = formateLeaveRequest(leaveReq)
        
        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"UserLeaveRequest.html" , { 
            "slug" : slug ,
            # "org": org ,
            "user" : currentUser,
            # "orgSize":orgSize,
            "afterSlug":"add",
            # "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"users",
            "page" : "leave-request" ,
            "totalRequests" : np.arange(0, math.ceil(len(leaveReq)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "deleteAction":deleteAction,
            "columnCount":7,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search
             })
        
    except Exception as e:
        return HttpResponseServerError(e)
    
def addLeaveRequest(request , slug):
    try:
        currentUser = request.session["user"]

        userData = get_object_or_404(Users , _id = currentUser["_id"])
        form = LeaveRequestForm()
        return render(request , "AddLeaveRequest.html" , {
            'slug' : slug,
            'form' : form
            })
    except Exception as e:
        return HttpResponse(e)
    
def editLeaveRequest(request , slug , id):
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])

        leaveReq = get_object_or_404(LeaveRequest , id = id , createdBy = userData)

        return render(request , "LeaveRequestDetails.html" , {
            'data' : leaveReq
        })
    except Exception as e:
        return HttpResponseServerError(e)

def editLeaveRequestStatus(request , slug , id):
    try:
        status 
        pass
    except Exception as e:
        return HttpResponse(e)

def deleteLeaveRequest(request ,slug , id):
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])

        LeaveRequest.objects.filter(id = id , createdBy = userData).delete()
        return HttpResponseRedirect(f"/users/leave-request/{slug}")
    except Exception as e:
        return HttpResponseServerError(e)