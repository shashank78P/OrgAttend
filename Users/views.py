import math
import random
import numpy as np
import json
import os
from dateutil import parser
from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse ,HttpResponseServerError , HttpResponseRedirect, JsonResponse ,Http404 , HttpResponseForbidden, QueryDict
from django.contrib import messages
from django.contrib.auth.hashers import make_password , check_password
from .forms import LeaveRequestForm, UserProfileEdit, changePasswordForm, signUpForm , logInForm, signUpForm2
from .models import Address, Users 
from Organization.models import Attendance, Employee, Job_title, LeaveRequest, Organization, OwnerDetails, Team, TeamMember
from datetime import datetime , timedelta, timezone
import jwt
from dotenv import load_dotenv
from django.db.models import Q
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string

def sendmail(toEmail , subject , htmlContent ):
    try:
        message = Mail(
        from_email='dailydash155@gmail.com',
        to_emails=toEmail,
        subject=subject,
        html_content=htmlContent)
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        raise Exception(e)

def editUserData(request , slug) :
    try:
        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])

        if(slugUser._id != userData._id):
            return HttpResponseForbidden("You dont have a access.")
        

        if(request.method == "POST"):
            form = UserProfileEdit(request.POST)
            if form.is_valid():
                logo = request.FILES.get('logo' , False)
                firstName = request.POST["firstName"]
                middleName = request.POST["middleName"]
                lastName = request.POST["lastName"]
                DOB = request.POST["DOB"]
                phoneNumber = request.POST["phoneNumber"]
                city = request.POST["city"]
                state = request.POST["state"]
                country = request.POST["country"]
                code = request.POST["code"]


                if logo != False:
                    userDataToUpdate = Users.objects.get(_id = userData._id)    
                    userDataToUpdate.logo = logo
                    userDataToUpdate.save()

                try:
                    if userData.address_id is None:
                        add = Address(city= city,state= state,country= country,code= code)
                        add.save()
                        Users.objects.filter(_id = userData._id).update(address = add)
                        pass
                    else:
                        Address.objects.filter(id = userData.address_id).update(city= city,state= state,country= country,code= code)

                    Users.objects.filter(_id = userData._id).update(
                        firstName = firstName,
                        middleName = middleName,
                        lastName = lastName,
                        DOB = DOB, 
                        phoneNumber = phoneNumber
                    )
                    return HttpResponseRedirect(f"/users/{slug}")
                except Exception as e:
                    if 'UNIQUE constraint failed' in str(e):
                        form.add_error("phoneNumber" , "Phone number already exists.")
                    return render(request ,"EditUserProfile.html" , { 
                        'form' : form , 
                        'slug' : slug
                    })
            else:
                return render(request ,"EditUserProfile.html" , { 
                    'form' : form , 
                    'slug' : slug
                })

        elif(request.method == "GET"):
            query_dict = QueryDict(mutable=True)
            if(userData.address is not None):
                address = Address.objects.filter(id = userData.address.id)
                query_dict.appendlist("city" , address[0].city)
                query_dict.appendlist("state" , address[0].state)
                query_dict.appendlist("country" , address[0].country)
                query_dict.appendlist("code" , address[0].code)
            
            query_dict.appendlist("logo" , userData.logo)
            query_dict.appendlist("firstName" , userData.firstName)
            query_dict.appendlist("middleName" , userData.middleName)
            query_dict.appendlist("lastName" , userData.lastName)
            query_dict.appendlist("DOB" , userData.DOB)
            query_dict.appendlist("phoneNumber" , userData.phoneNumber)
            
            form = UserProfileEdit(query_dict)
            return render(request ,"EditUserProfile.html" , { 'form' : form , "slug" : slug })
    except Exception as e:
            HttpResponseServerError(e)

def signUp(request) :
    try:
        if(request.method == "POST"):
            form = signUpForm(request.POST)
            if form.is_valid():
                email = request.POST["email"]

                user = Users.objects.filter(email=email, password__isnull=False).first()

                if( user is not None ):
                    form.add_error("email" , "User with this email already exist.")
                    return render(request ,"RequestForOtp.html" , { 'form' : form })
                
                otp = random.randint(1000 , 9999)
                subject = "Response to the request of OTP"
                htmlContent = f"""
                    <h1>Stay In Time Tracker</h1>
                    <p>This mail is to the response to request made for opening an account in <b>Stay In Time Tracker</b></p>
                    <p>Here is your OTP : <strong>{otp}</strong></p>
                    <p>Thank you, for your interest.</p>
                    <br/>
                    <p style="color : red">This otp is only valid for 15min.</p>
                """
                sendmail(email , subject , htmlContent)

                Users.objects.update_or_create(email=email, defaults={'otp': otp ,'lastOtpSentAt' :datetime.now(timezone.utc)})
                return HttpResponseRedirect("/users/sign-up-2")
            else:
                return render(request ,"RequestForOtp.html" , { 'form' : form })

        elif(request.method == "GET"):
            form = signUpForm()
            return render(request ,"RequestForOtp.html" , { 'form' : form })
    except Exception as e:
            HttpResponseServerError(e)

def signUp2(request) :
    try:
        if(request.method == "POST"):
            form = signUpForm2(request.POST)
            # data = request.POST
            email=request.POST["email"]
            otp=request.POST["otp"]

            userData = get_object_or_404(Users , email = email)
            otpSentAt = userData.updatedAt

            # Get the current time in UTC (timezone-aware)
            now = datetime.now(timezone.utc)

            # Calculate the time difference
            time_difference = now - otpSentAt
            
            if time_difference.total_seconds() > 15 * 60:
                form.add_error("otp" ,"Invalid otp (try to generate new OTP)")
                return render(request ,"SignUp.html" , { 'form' : form })

            if(otp != userData.otp):
                form.add_error("otp" ,"Invalid otp")
                return render(request ,"SignUp.html" , { 'form' : form })

            password=request.POST["password"]
            confirmPassword=request.POST["confirmPassword"]

            if(password != confirmPassword):
                form.add_error("confirmPassword" ,"Passwords not matched")
                return render(request ,"SignUp.html" , { 'form' : form })
            
            if form.is_valid():
                Users.objects.filter(email = email).update(
                    firstName = request.POST["firstName"],
                    middleName = request.POST["middleName"],
                    lastName = request.POST["lastName"],
                    password = make_password(request.POST["password"]),
                    otp = None,
                )
                return HttpResponseRedirect("/users/log-in")
            else:
                return render(request ,"SignUp.html" , { 'form' : form })

        elif(request.method == "GET"):
            form = signUpForm2()
            return render(request ,"SignUp.html" , { 'form' : form })
    except Exception as e:
            return HttpResponseServerError(e)

def login(request) :
    try:
        if(request.method == "POST"):
            form = logInForm(request.POST)
            password=request.POST["password"]
            email=request.POST["email"]

            user = Users.objects.filter(email = email)

            if(len(user) == 0):
                form.add_error("password" ,"User with this mail not exists!")
                return render(request ,"LogIn.html" , { 'form' : form })
            
            user = user[0]

            if(check_password(password , user.password)):
                response = HttpResponseRedirect(f"/users/{user.slug}")
                # render(request ,"Profile.html" , { "slug" : "" })
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
        return render(request ,"LogIn.html", { 'form' : form })
        # HttpResponseServerError("Internal Server error")

def getOrgById(request , id , userId):
    try:
        if(id == -1):
            orgDetails = OwnerDetails.objects.filter(userId =userId).first()
            empDetails = Employee.objects.filter(employee =userId).first()
            if orgDetails is not None:
                id = orgDetails._id 
            elif empDetails is not None:
                id = empDetails.Organization._id
        org = get_object_or_404(Organization , _id = id)
        return org
    except Exception as e:
        HttpResponseServerError(e)

def ChangePassword1(request):
    try:
        if(request.method == "POST"):
            email = request.POST.get("email" , False)
            if(not email):
                form = signUpForm()
                return render(request ,"ChangePassword.html" , { 
                    'form' : form ,
                })
            
            userData = getUserByEmail(email)

            otp = random.randint(1000 , 9999)
            email = userData.email
            subject = "Here is the OTP for password change"
            htmlContent = f"""
                <h1>Stay In Time Tracker</h1>
                <p>This mail is to the response to request made for password change <b>Stay In Time Tracker</b></p>
                <p>Here is your OTP : <strong>{otp}</strong></p>
                <p>Thank you, for your interest.</p>
                <p style="color : red">This otp is only valid for 15min.</p>
            """
            # sendmail(email , subject , htmlContent)
            
            userData.otp = otp
            userData.lastOtpSentAt = datetime.now(timezone.utc) 
            userData.save()
            return HttpResponseRedirect(f"/users/change-password")
        else:
            form = signUpForm()
            return render(request ,"ChangePassword.html" , { 
                'form' : form ,
                'action' : "/users/change-password-pre"
            })
    except Exception as e:
        return HttpResponseForbidden(e)

def ChangePassword(request):
    try:
        if(request.method == "POST"):
            form = changePasswordForm(request.POST)
            if form.is_valid():
                otp = request.POST.get("otp" , False)
                email = request.POST.get("email" , False)
                password = request.POST.get("password" , False)
                confirmPassword = request.POST.get("confirmPassword" , False)

                if(not (otp and password and confirmPassword and email)):
                    return render(request ,"ChangePassword.html" , { 
                    'form' : form ,
                    'action' :"/users/change-password"
                })

                if(confirmPassword != password):
                    form.add_error("confirmPassword" , "Password not matched")
                    return render(request ,"ChangePassword.html" , { 
                    'form' : form ,
                    'action' :"/users/change-password"
                })

                userData = Users.objects.get(email = email)
                if(otp != userData.otp):
                    form.add_error("otp" , "Invalid otp")
                    return render(request ,"ChangePassword.html" , { 
                    'form' : form , 
                    'action' :"/users/change-password"
                })

                currentDateTime = datetime.now(timezone.utc)

                diff = currentDateTime - userData.lastOtpSentAt

                if(diff.total_seconds() > 15*60):
                    form.add_error("otp" , "Invalid OTP")
                    return render(request ,"ChangePassword.html" , { 
                    'form' : form , 
                    'action' :"/users/change-password"
                })

                userData.password = make_password(request.POST["password"])
                userData.otp = None
                userData.lastOtpSentAt = None
                userData.save()
                return HttpResponseRedirect(f"/users/{userData.slug}")
            else:
                form = changePasswordForm(request.POST)
                return render(request ,"ChangePassword.html" , { 
                    'form' : form ,
                    'action' :"/users/change-password"
                })
        else:
                form = changePasswordForm()
                return render(request ,"ChangePassword.html" , { 
                    'form' : form ,
                    'action' :"/users/change-password"
                })
            
        
    except Exception as e:
        return HttpResponseForbidden(e)

def isUserOwner(currUserId , orgId):
    query1 = f"""
        SELECT 
            * 
        from 
            Organization_ownerdetails 
        where 
            userId_id = {currUserId} AND 
            OrganizationId_id = {orgId};
        """
    return OwnerDetails.objects.raw(query1)

def getCommonTeamIdsOfUsers(request , currUserId , originalUserId , orgId):
    try:
        
        isOwner = isUserOwner(currUserId , orgId)
        commonTeamIds = []
        
        leaderCoLeaderQuery = ""

        # if not owner check for leader or co-leader
        if(len(isOwner) <= 1):
            leaderCoLeaderQuery = ' role in ("LEADER" , "CO-LEADER") AND '

        query2 = f"""
            SELECT 
                 TeamId_id,
                 id
                FROM Organization_teammember
                WHERE 
                userId_id = {originalUserId}
                AND
                TeamId_id in
                (SELECT
                 TeamId_id
                FROM Organization_teammember
                WHERE
                	OrganizationId_id ={orgId} AND
                    {leaderCoLeaderQuery}
                    userId_id = {currUserId}
                );
        """
        commonTeams = TeamMember.objects.raw(query2)

        if(len(commonTeams) <= 1):
            return HttpResponseForbidden("You don't have a access.")
    
        for ids in commonTeams:
            commonTeamIds.append(ids.TeamId_id)
        
        if len(commonTeamIds) == 1:
            commonTeamIds= list(commonTeamIds)
            commonTeamIds.append(-1)
            commonTeamIds.append(-1)

        return tuple(commonTeamIds)
    except Exception as e:
        return HttpResponseForbidden(e)

def getTeamIds(request , userData , slugUser , org):
    teamIds=[]
    if(slugUser._id != userData._id):
        teamIds = getCommonTeamIdsOfUsers(request , userData._id , slugUser._id , org._id)
    else:
        # query1 = f"""
        #         SELECT 
        #             * 
        #         from 
        #             Organization_teammember 
        #         where 
        #             userId_id = {userData._id} AND 
        #             OrganizationId_id = {org._id};
        # """
        teamIds = TeamMember.objects.filter(OrganizationId = org, userId = userData).values_list('TeamId', flat=True).distinct()
        # ids = TeamMember.objects.raw(query1)
        # for i in ids:
        #     teamIds.append(i.TeamId_id)
    return teamIds

def getUsersJobTitle(teamIds , userId ,orgId):
    teamIds = list(teamIds)
    if len(teamIds) <= 1:
        teamIds = list(teamIds)
        teamIds.append(-1)
        teamIds.append(-1)

    query = f"""
            select 
                title,
                id
            from Organization_job_title
            where 
            id in 
            (select 
                DISTINCT(e.jobTitle_id)
            FROM 
                Organization_team as t,
                Organization_teammember as tm,
                Organization_employee as e
            WHERE
                t.id IN {tuple(teamIds)} AND
                e.employee_id = {userId} AND
                e.Organization_id = {orgId} AND
                e.Organization_id = t.OrganizationId_id AND
                tm.OrganizationId_id = t.OrganizationId_id AND
                e.employee_id = tm.userId_id
            );
        """
    return Job_title.objects.raw(query)

def home(request , slug) :
    try:    
        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])
        org = getOrgById(request , user["currentActiveOrganization"] , slugUser)
        userImg = f"{os.environ.get('FRONTEND')}/media/{slugUser.logo}"

        if(org == None):
            return render(request , "NoOrganizationUserInfo.html" , {
            'slug' : slug ,
            "user" : slugUser , 
            "userProfilePic" : f"{ userImg if slugUser.logo != None else False}",
            "endpoint":"users" ,
            "isOriginalUser" : "true" if slugUser._id == userData._id else "false",
            "baseUrl" : os.environ.get('FRONTEND')
            })
        if(not (bool(org)  and bool(userData) and bool(slugUser)) ):
            return HttpResponseForbidden("You dont have a access")

        teamIds = getTeamIds(request , userData , slugUser , org)
        

        isowner = isUserOwner(slugUser._id , org._id)
        # if(len(teamIds) == 0):
        #     return HttpResponseForbidden("You don't have a access")
        
        userJobTitleData = getUsersJobTitle(teamIds , slugUser._id , org._id)
        userJobTitle = ""


        for job in userJobTitleData:
            if( userJobTitle == ""):
                userJobTitle = job.title
            else: 
                userJobTitle += f" | {job.title}"
                    
        navOptions = {
            "leave_request" : True,
            "attendance" : True
        }
        return render(request ,"Home.html" , {
            "navOptions" : navOptions,
            'slug' : slug ,
            "user" : slugUser , 
            "userProfilePic" : f"{ userImg if slugUser.logo != None else False}",
            "isOwner" : len(isowner) > 0,
            "userJobTitle" : userJobTitle,
            "endpoint":"users" ,
            "isOriginalUser" : "true" if slugUser._id == userData._id else "false",
            "baseUrl" : os.environ.get('FRONTEND')
        })
    except Exception as e:
        return HttpResponseServerError(e)
    
def calculatePercentageForLeaveTye(data):
    result = {}
    resultPercentage = {}
    totalLeaves = 0
    for i in data:
        totalLeaves = totalLeaves + i.total
        result[i.leaveType] = i.total
    if(totalLeaves != 0):
        for i in data:
            resultPercentage[i.leaveType] = round(((i.total / totalLeaves) * 100))
    return JsonResponse({
        "result" : result,
        "percentage" : resultPercentage
    })

def getLeaveTypeInsightOfUser(request  , slug , fromDate , toDate):
    try:
        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])
        org = getOrgById(request , user["currentActiveOrganization"] ,slugUser)
        
        teamIds = getTeamIds(request , userData , slugUser , org)

        if(len(teamIds) < 0):
            return HttpResponseForbidden("You don't have a access.")
        if(len(teamIds) <= 1):
            teamIds = list(teamIds)
            teamIds.append(-1)
            teamIds.append(-1)

        fromDate = fromDate.split("T")[0]
        toDate = toDate.split("T")[0]
        
        query = f"""
        SELECT 
        count(*) as total,
        l.leaveType,
        id
        FROM Organization_leaverequest as l
        where 
        id <> -1 and
        Organization_id = {org._id} AND
        teamId_id in {tuple(teamIds)} AND
        status = "ACCEPTED" AND
        fromDate BETWEEN '{fromDate}' AND '{toDate}'
        AND
        toDate BETWEEN '{fromDate}' AND '{toDate}'
        GROUP BY leaveType;
    """
        
        data = LeaveRequest.objects.raw(query)

        return calculatePercentageForLeaveTye(data)        

    except Exception as e:
        return HttpResponseServerError(e)
    
def getAttendance(request , slug , teamIds ,userData , year):
    try:
        teamIds = list(teamIds)
        if len(teamIds) <= 1:
            teamIds = list(teamIds)
            teamIds.append(-1)
            teamIds.append(-1)
        DayInNumber = {
            'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6
        }



        att_data = {1 : {},2: {},3: {},4: {},5: {},6: {},7: {},8: {},9: {},10: {},11: {},12: {}}

            # a.TeamId_id as TeamId,
        fromDate = datetime(year, 1, 1).strftime("%Y-%m-%d")
        toDate = datetime(year+1, 1, 1) - timedelta(days=1)
        toDate = toDate.strftime("%Y-%m-%d")
        query  = f"""
        SELECT  
            takenAt AS takenAt,
            SUM(CASE WHEN attendance = 1 THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN attendance = 0 THEN 1 ELSE 0 END) AS absent,
            COUNT(takenAt) AS total,
            id
        FROM 
            Organization_attendance AS a
        where 
            id <> -1 and 
            TeamId_id in {tuple(teamIds)} and
            a.userId_id = {userData._id} AND
            takenAt between '{fromDate}' and '{toDate}'
        GROUP BY 
            takenAt ORDER BY takenAt;
        """

        data = Attendance.objects.raw(query)

        for d in data:
            # x = date(d.takenAt)
            att_data[d.takenAt.month][d.takenAt.day] = {
                    'percentage' : math.ceil(d.present / d.total) * 100,
                    "validCell" : True , "noAttendance" : False,
                    "takenAt" : d.takenAt
            }

        
        finalCalendarData = {"1": {},"2": {},"3": {},"4": {},"5": {},"6": {},"7": {},"8": {},"9": {},"10": {},"11": {},"12": {}}

        # i is for month
        for i in range(12):
            start_date = datetime(year, i + 1, 1)
            last_date = "";
            
            if(i == 11):
                last_date = datetime(year+1, 1, 1) - timedelta(days=1)
            else:
                last_date = datetime(year, i + 2, 1) - timedelta(days=1)

            start_day = start_date.strftime('%a')
            last_day = last_date.strftime('%a')

            number_of_days_in_month = last_date.day
            total_number_of_div = DayInNumber[(start_day)] + number_of_days_in_month + abs(DayInNumber[last_day] - 6)


            defaultAttenance = { 'percentage' : 0 , "validCell" : False , "noAttendance" : False}
            day = 1;
            for j in range(total_number_of_div):
                if (j >= DayInNumber[start_day] and j < (total_number_of_div -(6 - DayInNumber[last_day]))):
                    finalCalendarData[str(i+1)][str(j)] = att_data[i+1].get(day , { 'percentage' : 0 ,  "validCell" : True , "noAttendance" : True })
                    day = day +1
                else:
                    finalCalendarData[str(i+1)][str(j)] = defaultAttenance
        return finalCalendarData
    except Exception as e:
        return HttpResponseServerError(e)


def getAttendanceByTeamOrg(request , slug , fromDate , toDate):
    try:
        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])
        org = getOrgById(request , user["currentActiveOrganization"],slugUser)
        
        teamIds = getTeamIds(request , userData , slugUser , org)

        if(len(teamIds) < 0):
            return HttpResponseForbidden("You don't have a access.")
        
        teamIds = list(teamIds)
        if len(teamIds) <= 1:
            teamIds = list(teamIds)
            teamIds.append(-1)
            teamIds.append(-1)

        fromDate = fromDate.split("T")[0]
        toDate = toDate.split("T")[0]
        
        query = f"""
                SELECT
                    t.id as teamId,
                    a.id as id,
                    t.name as teamName,
                    COUNT(*) as total,
                    SUM(CASE WHEN a.attendance = 1 THEN 1 ELSE 0 END) as attendance
                FROM 
                    Organization_team as t
                LEFT JOIN 
                    Organization_attendance as a ON t.id = a.TeamId_id
                WHERE 
                    t.id IN {tuple(teamIds)} AND
                    a.Organization_id = {org._id} AND 
                    a.takenAt BETWEEN '{fromDate}' AND '{toDate}'
                GROUP BY 
                    t.id, t.name;
        """
        data = Attendance.objects.raw(query)

        label = []
        total = []

        for d in data:
            label.append(d.teamName)
            total.append( round((d.attendance / d.total) * 100 ) if d.total != 0 else 0 )

        return JsonResponse(
            {
                "label" : label,
                "total" : total
            } 
        )
        
    except Exception as e:
        return HttpResponseForbidden(e)

def homePage(request):
    try:
        user = request.session["user"]
        # org = Organization.objects.get(_id = user["currentActiveOrganization"])
        # slug = org.slug
        return HttpResponseRedirect(f"/users/{user['slug']}")
    except Exception as e:
        return HttpResponseServerError(e)

def setCurrentActiveOrganization(request):
    try:
        if(request.method == "POST"):
            userData = request.session["user"]
            data = json.loads(request.body.decode('utf-8'))
            user = Users.objects.get(_id = userData["_id"])

            org = get_object_or_404(Organization , slug = data["slug"])
            user.currentActiveOrganization =  int(org._id)
            sessionUser = request.session['user']
            sessionUser['currentActiveOrganization'] = int(org._id)
            user.save()
            return JsonResponse({ "data" : "" , "message" : "Switched sucessfully" })
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)

def attendanceHistory(request , slug) :
    try:
        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])
        org = getOrgById(request , user["currentActiveOrganization"] , slugUser)
        
        teamIds = getTeamIds(request , userData , slugUser , org)

        if(len(teamIds) < 0):
            return HttpResponseForbidden("You don't have a access.")
        
        userJobTitleData = getUsersJobTitle(teamIds , slugUser._id , org._id)
        userJobTitle = ""


        for job in userJobTitleData:
            if( userJobTitle == ""):
                userJobTitle = job.title
            else: 
                userJobTitle += f" | {job.title}"
        isowner = isUserOwner(slugUser._id , org._id)
        userImg = f"{os.environ.get('FRONTEND')}/media/{slugUser.logo}"

        navOptions = {
            "leave_request" : True,
        }

        today = datetime.today()
        year = today.year

        if (request.method == "POST" and request.POST["year"] is not None):
            year = int(request.POST["year"])

        attendanceDataOfTeam = getAttendance(request , slug , teamIds=teamIds ,userData=slugUser ,year=year)

        return render(request ,
                    "AttendanceHistory.html" , 
                    {
                        "navOptions" : navOptions,
                         'slug' : slug , 
                         "user" : slugUser , 
                         "endpoint":"users" , 
                         "baseUrl" : os.environ.get('FRONTEND'),
                         "att_data" : attendanceDataOfTeam,
                         "year" : year,
                         "userProfilePic" : f"{ userImg if slugUser.logo != None else False}",
                         "isOwner" : len(isowner) > 0,
                         "userJobTitle" : userJobTitle,
                         "isOriginalUser" : "true" if slugUser._id == userData._id else "false"
                      })
    except Exception as e:
            HttpResponseServerError(e)

def getAttendanceInDetailsByDay(request , slug , takenAt):
    try:
        takenDate = parser.parse(takenAt).date()

        user = request.session["user"]
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = user["slug"])
        org = getOrgById(request , user["currentActiveOrganization"] , slugUser)
        
        teamIds = getTeamIds(request , userData , slugUser , org)

        if(len(teamIds) < 0):
            return HttpResponseForbidden("You don't have a access.")
        
        teamIds = list(teamIds)
        if len(teamIds) <= 1:
            teamIds = list(teamIds)
            teamIds.append(-1)
            teamIds.append(-1)

        query = f"""
            SELECT 
                t.id,
                t.name as teamName,
                t.checkInTime as checkInTime,
                t.checkOutTime as checkOutTime,
                takenAt AS takenAt,
                a.attendance as attendance
            FROM 
                Organization_team as t
            LEFT JOIN 
                Organization_attendance as a ON t.id = a.TeamId_id
            WHERE 
                t.id IN {tuple(teamIds)} AND
                a.Organization_id = {org._id} AND 
                a.takenAt ='{takenDate}' AND
                a.userId_id = '{userData._id}';
        """


        data = Team.objects.raw(query)

        
        userJobTitleData = getUsersJobTitle(teamIds , slugUser._id , org._id)
        userJobTitle = ""


        for job in userJobTitleData:
            if( userJobTitle == ""):
                userJobTitle = job.title
            else: 
                userJobTitle += f" | {job.title}"
        isowner = isUserOwner(slugUser._id , org._id)
        userImg = f"{os.environ.get('FRONTEND')}/media/{slugUser.logo}"
        # att_data = []

        # for d in data:
        #     att_data.append(d)
        
        return render(request ,"AttendanceDetailsCard.html" , {
            'slug' : slug ,
            "user" : slugUser , 
            "data" : data,
            "endpoint":"users" , 
            "baseUrl" : os.environ.get('FRONTEND'),
            "userProfilePic" : f"{ userImg if slugUser.logo != None else False}",
            "isOwner" : len(isowner) > 0,
            "userJobTitle" : userJobTitle,
            "isOriginalUser" : "true" if slugUser._id == userData._id else "false"
        })
    except Exception as e:
        return HttpResponseServerError(e)

def add(request) :
    try:
        return render(request ,"SignUp.html")
    except Exception as e:
            HttpResponseServerError(e)

def edit(request , slug) :
    try:
        return render(request ,"Edit.html" , { 'slug' : slug })
    except Exception as e:
            HttpResponseServerError(e)

def delete(request , slug) :
    try:
        return render(request ,"delete.html" , { 'slug' : slug })
    except Exception as e:
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
        for i in  range(0,len(leaveRequestData)):
            data = leaveRequestData[i]

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
        slugUser = get_object_or_404(Users , slug = slug)
        userData = get_object_or_404(Users , slug = currentUser["slug"])
        org = getOrgById(request , currentUser["currentActiveOrganization"], slugUser)
        
        teamIds = getTeamIds(request , userData , slugUser , org)

        if(len(teamIds) < 0):
            return HttpResponseForbidden("You don't have a access.")

        search=""
        rows=10
        page=0
        data = request.POST


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"])
        


        skip = page*rows

        leaveReq = LeaveRequest.objects.filter(
            Q(createdBy = userData) & Q(Organization = org) &
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
        navOptions = {
            "leave_request" : True,
        }


        tableTitle , tableData  = formateLeaveRequest(leaveReq)

        userJobTitleData = getUsersJobTitle(teamIds , slugUser._id , org._id)
        userJobTitle = ""


        for job in userJobTitleData:
            if( userJobTitle == ""):
                userJobTitle = job.title
            else: 
                userJobTitle += f" | {job.title}"
        isowner = isUserOwner(slugUser._id , org._id)
        userImg = f"{os.environ.get('FRONTEND')}/media/{slugUser.logo}"
        
        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"UserLeaveRequest.html" , { 
            "slug" : slug ,
            "user" : slugUser,
            "afterSlug":"add",
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"users",
            "page" : "leave-request" ,
            "totalRequests" : np.arange(0, math.ceil(len(leaveReq)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "addAction" : True,
            "deleteAction":deleteAction,
            "navOptions" : navOptions,
            "columnCount":7,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search,
            "isOriginalUser" : "true" if slugUser._id == userData._id else "false",
            "userProfilePic" : f"{ userImg if slugUser.logo != None else False}",
            "isOwner" : len(isowner) > 0,
            "userJobTitle" : userJobTitle,
             })
        
    except Exception as e:
        return HttpResponseServerError(e)
    
def addLeaveRequest(request , slug):
    try:
        currentUser = request.session["user"]
        org = get_object_or_404( Organization, _id = currentUser["currentActiveOrganization"])
        userData = get_object_or_404(Users , _id = currentUser["_id"])
        form = LeaveRequestForm( organization = org,user = userData)
        return render(request , "AddLeaveRequest.html" , {
            'slug' : slug,
            'form' : form
            })
    except Exception as e:
        return HttpResponse(e)
    
def seeLeaveRequest(request , slug , id):
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])

        leaveReq = get_object_or_404(LeaveRequest , id = id , createdBy = userData)

        return render(request , "LeaveRequestDetails.html" , {
            'data' : leaveReq,
            "slug" : slug,
            'id' : id
        })
    except Exception as e:
        return HttpResponseServerError(e)
    
def deleteLeaveRequest(request ,slug , id):
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])

        LeaveRequest.objects.filter(id = id , createdBy = userData).delete()
        return HttpResponseRedirect(f"/users/leave-request/{slug}")
    except Exception as e:
        return HttpResponseServerError(e)

def logout(request):
    try:
        currentUser = request.session["user"]
        userData = get_object_or_404(Users , _id = currentUser["_id"])
        response = HttpResponseRedirect(f"/users/log-in")
        response.set_signed_cookie(
                        'authorization' , f"Bearer " ,
                        salt="attendance123",
                        expires= datetime.utcnow() + timedelta(days= 1) 
        )
        return response;
    except Exception as e:
        return HttpResponseServerError(e)
