import math
import os
from django.db import IntegrityError
from django.http import QueryDict
from django.http import HttpResponseServerError , HttpResponseNotAllowed, JsonResponse , Http404 , HttpResponseRedirect
from django.shortcuts import render , get_object_or_404
import requests
from Organization.forms import createOrganizationForm, createTeamForm , addEmployeeForm , addJobTitleForm , ChangeEmployeeRoleInTeam , addEmployeeToTeam, editEmployeeForm
from Organization.models import Attendance, LeaveRequest, Organization ,OwnerDetails , Team ,TeamMember , Employee , Job_title
from Users.forms import LeaveRequestForm
from Users.models import Address, Users
from Users.views import formateLeaveRequest, getUserByEmail
from django.db.models import Q
from datetime import date, datetime, timedelta
from django.db.models import Count
import numpy as np
from dateutil import parser

def isOwner(org , user):
    return OwnerDetails.objects.filter(OrganizationId = org , userId = user).values_list('OrganizationId', flat=True).distinct().exists()

def isLeaderOrCoLeader(team , org , user):
    return TeamMember.objects.filter(TeamId = team ,role__in = ["LEADER" , "CO-LEADER"] , OrganizationId =org , userId = user).exists()

def getTeamIdList(org , user):
    return TeamMember.objects.filter(role__in = ["LEADER" , "CO-LEADER"] , OrganizationId =org , userId = user).values_list('TeamId', flat=True).distinct()

def getAllUserIdListOfOrgForUser(org , user):
    print("getAllUserIdListOfOrgForUser")
    teamIdList = getTeamIdList(org , user)
    print(teamIdList)
    userList = TeamMember.objects.filter(TeamId__in = teamIdList).values_list('userId', flat=True).distinct()
    print(userList)
    return userList

def isLeaderOrCoLeaderInAtleastOneTeam(org , user):
    print("isLeader in atleast on company")
    print(TeamMember.objects.filter(role__in = ["LEADER" , "CO-LEADER"] ))
    return TeamMember.objects.filter(role__in = ["LEADER" , "CO-LEADER"] , OrganizationId =org , userId = user).exists()

def getOrgBySlug(request , slug):
    try:
        print(slug)
        org = get_object_or_404(Organization , slug = slug)
        return org
    except Exception as e:
        print(e)
        HttpResponseServerError(e)

# Create your views here.
def createOrganization(request):
    try:
        print(request.method)
        if(request.method == "POST"):
            form = createOrganizationForm(request.POST , request.FILES)
            data = request.POST
            print(request.POST)

            if form.is_valid():
                # owner datails
                temp_owners = data["ownersDetails"]
                temp_owners = temp_owners.split(",")
                owners=[]
                for email in temp_owners:
                    owners.append(email)
    
                print("checking for user existence")
                for email in owners:
                    print(email)
                    try:
                        user = Users.objects.get(email = email.strip())
                        print(user)
                    except Users.DoesNotExist:
                        form.add_error("ownersDetails" ,f"user with this email ({email}) not exist")
                        return render(request ,"CreateOrganization.html", { 'form' : form })
                    
                    address = Address(city = data["city"], state = data["state"], country = data["country"], code = data["code"])
                    print(address)
                    address.save()
                    print("address save")

                    logo = request.FILES.get('logo' , False)
        
                    org = Organization( 
                        name=data['name'],
                        address=address,
                        webSiteLink=data['webSiteLink'],
                        socialMediaLink=data['socialMediaLink'],
                        contactEmail=data['contactEmail'],
                        description=data['description'],
                        )
                    org.save()
                        # logo=request.FILES['logo'], 

                    if logo != False:
                        orgDataToUpdate = Organization.objects.get(_id = org._id)    
                        orgDataToUpdate.logo = logo
                        orgDataToUpdate.save()

                    print("org saved")
                    print(org )
    
                    for email in owners:
                        print("owners email")
                        print(email)
                        user = Users.objects.get(email = email.strip())
                        print(user)
                        ownersDetails = OwnerDetails(OrganizationId = org , userId = user)
                        print(ownersDetails)
                        ownersDetails.save()
                        print("ownersDetails save")
                    return HttpResponseRedirect(f"/organization/leave-request/{org.slug}")
            return render(request ,"CreateOrganization.html", { 'form' : form })
        else:
            form = createOrganizationForm()
            return render(request ,"CreateOrganization.html", { 'form' : form })
    except IntegrityError as e:
        print(e)
        print(e.args)  # This will print the error message
        print(e.args[0])  # This will print the error message
        form = createOrganizationForm(request.POST, request.FILES)
        for arg in e.args:
            if "contactEmail" in arg and "UNIQUE constraint failed" in arg:
                form.add_error("contactEmail" , "This email is already exist")
            if "name" in arg and "UNIQUE constraint failed" in arg:
                form.add_error("name" , "Organization name is already exist")
        return render(request ,"CreateOrganization.html", { 'form' : form })
    except Exception as e:
        print(e)
        form = createOrganizationForm()
        return render(request ,"CreateOrganization.html", { 'form' : form })
    

def companyProfile(request , slug):
    try:
        # print("called companyProfile")
        # user = request.session["user"]
        # org = Organization.objects.get(slug = slug)
        
        # orgSize = getOrgSize(org)
        # print(f"{os.environ.get('FRONTEND')}/media/{org.logo}")
        # userData = get_object_or_404(Users , _id = user["_id"])
        # isHeOwner = isOwner(org , userData)
        # isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org , userData)
        # navOptions = {
        #     "leave_request" : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
        #     'job_title' : isHeOwner ,
        #     'teams' : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
        #     'employees' : isHeOwner
        # }
        # return render(request ,"companyProfile.html" , 
        #     { 
        #         "slug" : slug ,
        #         "user" : user,
        #         "org": org ,
        #         "page" : "COMPANY_PROFILE" ,
        #         "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
        #         "orgSize" : orgSize,
        #         "endpoint":"organization",
        #         "navOptions":navOptions,
        #         "baseUrl" : os.environ.get('FRONTEND')
        #     }
        # )
        return HttpResponseRedirect(f"/organization/leave-request/{slug}")
    except Exception as e:
        return HttpResponseServerError(e)
        # return render(request ,"companyProfile.html")        

def companyRole(request , slug):
    try:
        return render(request ,"createEmployeeRole.html")
    except():
        return render(request ,"createEmployeeRole.html")

def saveTeamMemberData(request,user , form , role , team , orgId, createdBy):
    try:
        print("save team member user")
        print(user)
        print(type(user))
        print(team)
        print("teamMem")

        isDuplicate = TeamMember.objects.filter(userId_id = user._id , TeamId_id = team.id , OrganizationId_id = orgId._id )

        print(isDuplicate)

        if len(isDuplicate) >= 1:
            print("isDuplicate")
            return
        else:
            teamMem = TeamMember(
                userId = user,
                role = role,
                TeamId = team,
                OrganizationId = orgId,
                createdBy = Users.objects.get(_id = createdBy["_id"])
            )
            print(teamMem)
            teamMem.save()
            return 
        
    except Exception as e:
        print(e)
        HttpResponseServerError(e)
    
def getAllOrganizationList(request) :
    try:
        print("getAllOrganizationList")
        user = request.session["user"]
        print(user)

        # getting all companies of a user
        data = TeamMember.objects.filter( userId = user["_id"] ).values_list('OrganizationId', flat=True).distinct()
        data2 = OwnerDetails.objects.filter( userId = user["_id"] ).values_list('OrganizationId', flat=True).distinct()

        print(data)
        print(data2)
        all_org = []
        org_data = Organization.objects.filter(Q(_id__in = data) | Q(_id__in = data2))

        for org in list(org_data):
            all_org.append({
                'name' : org.name,
                '_id' : org._id,
                'slug' : org.slug
            })

        return JsonResponse({'data' : all_org})
    except Exception as e:
        print(e)
        HttpResponseServerError("Internal Server error")

def isUserPermittedToAdd(request):
    try:
        print("called isUserPermittedToAdd")
        user = request.session['user']
        print(user)
        print("getting org details")
        isPermited = OwnerDetails.objects.filter(Q(OrganizationId_id = user['currentActiveOrganization']) & Q(userId_id = user['_id']))  

        if(len(isPermited) == 0):
            return HttpResponseServerError("You don't an access to add")
        
    except:
        return HttpResponseNotAllowed("U don't have a permission")

def isCorrectTime(checkInTime , checkOutTime):
    print(checkInTime , checkOutTime)
    checkIn = checkInTime.split(" ")
    checkInTimeParam = checkIn[0].split(":")
    checkOut = checkOutTime.split(" ")
    checkOutTimeParam = checkOut[0].split(":")
    checkInHrs = int(checkInTimeParam[0])
    checkOutHrs = int(checkOutTimeParam[0])
    if checkIn[1] == "PM":
        checkInHrs += 12
    if checkOut[1] == "PM":
        checkOutHrs += 12
    
    if checkInHrs <= checkOutHrs:
        print("123")
        print((int(checkInTimeParam[1]) + 44 ) , int(checkOutTimeParam[1]))
        if checkInHrs == checkOutHrs and (int(checkInTimeParam[1]) + 44 ) < int(checkOutTimeParam[1]):
            return True
        else:
            return False
    else:
        return False
def isEmployeeInTeamAndOrgbyEmail(org, team , email):
    print("isEmployeeInTeamAndOrgbyEmail")
    user = Users.objects.filter(email = email).first()
    print(team)
    print(user)
    print(TeamMember.objects.filter(userId = user , OrganizationId = org , TeamId = team).exists())
    return TeamMember.objects.filter(userId = user , OrganizationId = org , TeamId = team).exists()
def isEmployeeInOrgbyEmail(org , email):
    user = Users.objects.filter(email = email).first()
    return Employee.objects.filter(employee = user , Organization = org).exists()


def createOrUpdate(request , user,slug , isEdit, teamId=""):
    try:
        isUserPermittedToAdd(request)
        print(request.POST)
        form = createTeamForm(request.POST)
        if form.is_valid():
            print("valid")
            data = request.POST
            print(data["checkInTime"])
            print(data["checkOutTime"])
            print(type(data["checkOutTime"]))

            if isCorrectTime(data["checkInTime"] , data["checkOutTime"]):
                form.add_error("checkOutTime" ,"Invalid CheckInTime and CheckOutTime , time interval between these must be of minimum 45min")
                title = "Create Team"
                if isEdit:
                    title = "Edit Team"
                return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : title})
            
            print(data)
            print(type(data))
            print(user)
            print('user["_id"]')
            print(user["_id"])
            createdBy = Users.objects.filter(_id = user["_id"]).first()
            print(createdBy)
            org_id = Organization.objects.filter(_id = user["currentActiveOrganization"]).first()
            print(org_id)

            #leader emails
            leader = data["leader"].split(",")
            print(leader)
            for email in leader:
                print("len(email)")
                print(len(email))
                if email != "" or len(email) != 0: 
                    if not isEmployeeInOrgbyEmail(org_id , email):
                        print("email isEmployeeInOrgbyEmail")
                        print(email)
                        form.add_error("leader" ,f"The user with this {email} is not exist in employee list")
                        return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})
                    print("leader isEdit")
                    if(isEdit):
                        print("isEdit = true")
                        team = Team.objects.filter(id = teamId).first()
                        if(isEmployeeInTeamAndOrgbyEmail(org_id, team,email)):
                            form.add_error("leader" ,f"The user with this {email} is already in team")
                            return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})
                
            #co-leader emails
            co_Leader = data["co_Leader"].split(",")
            for email in co_Leader:
                if  email != "" or len(email) != 0:
                    if not isEmployeeInOrgbyEmail(org_id , email):
                        form.add_error("co_Leader" ,f"The user with this {email} is not exist in employee list")
                        return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})

                    if(isEdit):
                        team = Team.objects.filter(id = teamId).first()
                        if(isEmployeeInTeamAndOrgbyEmail(org_id, team,email)):
                            form.add_error("co_Leader" ,f"The user with this {email} is already in team")
                            return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})

            #team_members emails
            team_members = data["team_members"].split(",")
            for email in team_members:
                if email != "" or len(email) != 0:
                    if not isEmployeeInOrgbyEmail(org_id , email):
                        form.add_error("team_members" ,f"The user with this {email} is not exist in employee list")
                        return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})

                    if(isEdit):
                        team = Team.objects.filter(id = teamId).first()
                        if(isEmployeeInTeamAndOrgbyEmail(org_id, team,email)):
                            form.add_error("team_members" ,f"The user with this {email} is already in team")
                            return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : "Create Team" if not isEdit else "Edit Team"})


            if not isEdit:
                team = Team(
                       name = data["name"],
                       OrganizationId = org_id,
                       checkInTime = datetime.strptime(data["checkInTime"], "%I:%M %p").time(),
                       checkOutTime = datetime.strptime(data["checkOutTime"], "%I:%M %p").time(),
                       description = data["description"],
                       createdBy = createdBy
                )
                team.save()
                
                # createrData = Users.objects.filter(email = user["email"])
                # saveTeamMemberData(request,createrData[0] , form , "LEADER" ,team , org_id,user)

            else:
                Team.objects.filter(id = teamId).update(
                       name = data["name"],
                       OrganizationId = org_id,
                       checkInTime = datetime.strptime(data["checkInTime"], "%I:%M %p").time(),
                       checkOutTime = datetime.strptime(data["checkOutTime"], "%I:%M %p").time(),
                       description = data["description"]
                )

            # leader
            print("team leader")
            print(data["leader"])
            leader = data["leader"].split(",")
            for email in leader:
                leader_Data = Users.objects.filter(email = email)
                if len(leader_Data) == 1:
                    saveTeamMemberData(request,leader_Data[0] , form , "LEADER",team , org_id , user)

            # co_Leader
            co_leader = data["co_Leader"].split(",")
            for email in co_leader:
                co_Leader_Data = Users.objects.filter(email = email)
                if len(co_Leader_Data) == 1:
                    saveTeamMemberData(request,co_Leader_Data[0] , form , "CO-LEADER",team , org_id , user)

            # team_members
            team_members = data["team_members"].split(",")
            for email in team_members:
                member_Data = Users.objects.filter(email = email)
                if len(member_Data) ==1:
                    saveTeamMemberData(request,member_Data[0] , form , "MEMBER" , team ,org_id,user)

            print(org_id.slug)
            return HttpResponseRedirect(f"/organization/teams/{slug}")
        
        else:
            title="Create Team"
            if isEdit:
                title = "Edit Team"
            return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , 'title' : title})
            
    except Exception as e:
        return HttpResponseServerError(e)

def createTeam(request,slug):
    try:
        print(request.method)
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        org = get_object_or_404( Organization, _id = user["currentActiveOrganization"])

        isHeOwner = isOwner(org , userData)

        if not isHeOwner:
            return HttpResponseNotAllowed()
        
        if(request.method == "POST"):
            return createOrUpdate(request , user,slug , False)
            
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , 'title' : "Create Team"})
    except():
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , 'title' : "Create Team"})

def formateTime12Hrs(time):
    time = str(time)
    time = time.split(":")
    hrs = int(time[0])
    print(hrs)
    if(hrs >= 12):
        time = f"{hrs % 12}:{time[1]} PM"
    else:  
        time = f"{hrs % 12}:{time[1]} AM"
    return time

def editTeam(request , slug , teamId):
    try:
        user = request.session["user"]
        print(user)
        userData = get_object_or_404(Users ,_id = user["_id"])
        org = getOrgBySlug(request , slug)
        print(org)
        team = get_object_or_404(Team , id = teamId)
        print(team)

        # only allowed to user who is owner or leader or co-leader
        if( not (isOwner(org , userData) | isLeaderOrCoLeader(team , org , userData))):
            return HttpResponseNotAllowed("You don't an access")

        if(request.method == "GET"):
            query_dict = QueryDict(mutable=True)
            query_dict.appendlist("checkInTime",formateTime12Hrs(team.checkInTime))
            query_dict.appendlist("checkOutTime",formateTime12Hrs(team.checkOutTime))
            query_dict.appendlist("description",team.description)
            query_dict.appendlist("name",team.name)
            form = createTeamForm(query_dict)
            return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug, 'title':"Edit Team" , 'teamId':teamId})
            
        elif(request.method == "POST"):
            return createOrUpdate(request,user,slug,True,teamId)

        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)

def delteTeam(request , slug , teamId):
    try:
        org = getOrgBySlug(request , slug)
        team = get_object_or_404(Team , id = teamId , OrganizationId = org)
        user = request.session["user"]
        print(user)
        userData = get_object_or_404(Users ,_id = user["_id"])
        # only allowed to user who is owner or leader or co-leader
        if( not (isOwner(org , userData) | isLeaderOrCoLeader(team , org , userData))):
            return HttpResponseNotAllowed("You don't an access")
        
        if(request.method == "POST"):
            Team.objects.filter(id = teamId , OrganizationId = org).delete()
            return HttpResponseRedirect(f"/organization/teams/{slug}")
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)

def getOrgSize(org):
    try:
        owner = OwnerDetails.objects.filter(OrganizationId = org).values_list('userId_id', flat=True).distinct()
        print(owner)
        member = TeamMember.objects.filter(Q(OrganizationId = org) & ~Q(userId_id__in = owner)).values_list('userId_id', flat=True).distinct()
        print(member)
        print("org.contactEmail")
        print(org.webSiteLink)
        orgSize = len(owner) + len(member)
        return orgSize
    except:
        return HttpResponseServerError()

def getTeamsFormatedData(TeamsData):
    tableTitle = ["name","Organization","checkInTime" , "checkOutTime","description","createdBy","createdAt"]
    tableData = []
    for i in  range(0,len(TeamsData)):
        team = TeamsData[i]
    
        tableData.append([ 
            f'{team.name}' ,
            f'{team.OrganizationId.name}',
            f'{team.checkInTime}',
            f'{team.checkOutTime}',
            f'{team.description}',
            f'{team.createdBy.firstName} {team.createdBy.middleName} {team.createdBy.lastName}',
            f'{team.createdAt}',
            f'{team.id}',
        ])
    return tableTitle , tableData

def leaveTypeInsightOfOrg(request , slug , fromDate , toDate):
    try:
        print("leaveTypeInsight")
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        org = getOrgBySlug( request , slug)
        isHeOwner = isOwner(org , userData)
        
        isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org , userData)

        if(not (isHeOwner or isHeLeaderOrCoLeaderInAtleastOneTeam)):
            return HttpResponseNotAllowed("You don't have an access.")
        
        interQuery = ""
        if(not isHeOwner):
            teamIds = getTeamIdList(org , userData)
            if len(teamIds) <= 1:
                teamIds.append(-1)
                teamIds.append(-1)
            interQuery = f" teamId_id in {tuple(teamIds)} AND"

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
        {interQuery}
        status = "ACCEPTED" AND
        fromDate BETWEEN '{fromDate}' AND '{toDate}'
        AND
        toDate BETWEEN '{fromDate}' AND '{toDate}'
        GROUP BY leaveType;
    """
        
        print(query)
        data = LeaveRequest.objects.raw(query)
        print(data)

        return calculatePercentageForLeaveTye(data)
        
    except Exception as e:
        print(e)
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
    print("result")
    print(result)
    print(resultPercentage)
    return JsonResponse({
        "result" : result,
        "percentage" : resultPercentage
    })

def leaveTypeInsight(request , slug , teamId , fromDate , toDate):
    try:
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        org = getOrgBySlug( request , slug)
        team = get_object_or_404(Team , id = teamId)
        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeader = isLeaderOrCoLeader(org=org , team=team , user=userData)

        if(not (isHeOwner | isHeLeaderOrCoLeader)):
            return HttpResponseNotAllowed("You don't have an access.")
        
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
        TeamId_id = {teamId} AND
        Organization_id = {org._id} AND
        status = "ACCEPTED" AND
        fromDate BETWEEN '{fromDate}' AND '{toDate}'
        AND
        toDate BETWEEN '{fromDate}' AND '{toDate}'
        GROUP BY leaveType;
    """
        
        print(query)
        data = LeaveRequest.objects.raw(query)
        print(data)
        
        return calculatePercentageForLeaveTye(data)
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def roleCountOfTeamsOrOrg( org_id, teamIds):
    queryBuilder = ""
    if(teamIds):
        queryBuilder = f" AND t.id in {teamIds} "

    query = f"""
        SELECT
            tm.role as role,
            count(tm.role) as total,
            tm.id
        FROM
            Organization_teammember as tm,
            Organization_team as t
        WHERE
            tm.OrganizationId_id = {org_id}  AND
            tm.TeamId_id = t.id
            {queryBuilder}
        GROUP BY
            tm.role;
    """

    data = TeamMember.objects.raw(query)
    co_Leader = 0
    leader = 0
    member = 0
    total = 0
    for i in data:
        total += i.total
        if i.role == "CO-LEADER":
            co_Leader = i.total
        if i.role == "LEADER":
            leader = i.total
        if i.role == "MEMBER":
            member = i.total
    return co_Leader,leader,member,total

def teams(request , slug):
    try:
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        org = getOrgBySlug(request , slug)
        search=""
        rows=10
        page=0
        data = request.POST
        print("=============== teams ==================")
        print(data)

        # only allowed to user who is owner or leader or co-leader
        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org , userData)
        print(isHeOwner)
        
        if( not ( isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam)):
            return HttpResponseNotAllowed("You don't an access")

        co_Leader = 0
        leader = 0
        member = 0
        total = 0
        avgAtt = 0

        if isHeOwner:
            co_Leader,leader,member,total = roleCountOfTeamsOrOrg(org_id= org._id , teamIds=False)
            avgAtt = getTeamAvgAttendance(request , slug , teamId=False , orgId=org._id)
        else:
            teamIds = getTeamIdList(org , userData)
            if len(teamIds) <= 1:
                teamIds.append(-1)
                teamIds.append(-1)
            co_Leader,leader,member,total = roleCountOfTeamsOrOrg(org_id= org._id , teamIds=tuple(teamIds))
            avgAtt = getTeamAvgAttendance(request , slug , tuple(teamIds) , org._id)


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"][0])
        

        print("data ===>")
        print(f"search= {search} rows= {rows} page= {page}")

        print(org)
        skip = page*rows
        orgSize = getOrgSize(org)

        print(f"skip {skip}")

        query = None
        
        if(isHeOwner):
            query = Q(OrganizationId = org)
        else:
            teamList=TeamMember.objects.filter( OrganizationId = org,  role__in = ["LEADER" , "CO-LEADER"] , userId = userData).values_list('TeamId',flat=True).distinct()
            query = (Q(OrganizationId = org) & Q(id__in = teamList))


        print("===================== query ====================")
        print(query)

        if(query == None) : 
            return HttpResponseNotAllowed()
        
        teamsData = Team.objects.filter(
            query &   
         (Q(name__icontains=search) |
        Q(checkInTime__icontains=search) |
        Q(checkOutTime__icontains=search) |
        Q(description__icontains=search) |
        Q(createdAt__icontains=search) |
        Q(createdBy__firstName__icontains=search) |
        Q(createdBy__middleName__icontains=search) |
        Q(createdBy__lastName__icontains=search) |
        Q(OrganizationId__name__icontains=search) |  
        Q(createdBy__email__icontains=search) |
        Q(createdBy__address__city__icontains=search) |
        Q(createdBy__address__state__icontains=search) |
        Q(createdBy__address__country__icontains=search) |
        Q(createdBy__address__code__icontains=search))
        ).order_by("-createdAt")
        
        tableTitle , tableData = getTeamsFormatedData(teamsData)
        print(teamsData)
        print(len(teamsData))

        openAction = True
        editAction = True
        deleteAction = True
        addAction = isHeOwner
        navOptions = {
            "leave_request" : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
            'job_title' : isHeOwner,
            'teams' : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
            'employees' : isHeOwner
        }

        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"Team.html" , { 
            "slug" : slug ,
            "navOptions" : navOptions,
            "org": org ,
            "user" : user,
            "orgSize":orgSize,
            "afterSlug":"add",
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"organization",
            "co_Leader" : co_Leader,
            "leader" : leader,
            "member" : member,
            "total" : total,
            "avgAtt":avgAtt,
            "page" : "teams" ,
            "teamsData" : teamsData[ skip :  skip + rows],
            "totalTeams" : np.arange(0, math.ceil(len(teamsData)/rows)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "addAction":addAction,
            "deleteAction":deleteAction,
            "columnCount":8,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "isOwner" : isHeOwner,
            "search":search
             })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def getTeamsMemebesFormatedData(TeamsMembersData , teamId , org):
    tableTitle = ["name","role","job-title","createdBy","createdAt"]
    tableData = []
    print(tableTitle)
    print("TeamsMembersData")
    print(TeamsMembersData)
    for i in  range(0,len(TeamsMembersData)):
        print(i)
        teamMember = TeamsMembersData[i]
        print("teamMember")
        print(teamMember)

        emp = Employee.objects.filter(employee = teamMember.userId, Organization = org).first()
        print("emp")
        print(emp)

        tableData.append([ 
            f'{teamMember.userId.firstName} {teamMember.userId.middleName} {teamMember.userId.lastName}',
            f'{teamMember.role}',
            f'{emp.jobTitle.title if emp is not None else ""}',
            f'{teamMember.createdBy.firstName} {teamMember.createdBy.middleName} {teamMember.createdBy.lastName}',
            f'{teamMember.createdAt}',
            f'{teamId}/{teamMember.id}/{emp._id if emp is not None else ""}',
        ])
    return tableTitle , tableData

def teamMembersDetails(request , slug , id):
    try:
        print("teamMembersDetails")
        user = request.session["user"]
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
        

        print("data ===>")
        print(id)
        print(search , rows)

        org = getOrgBySlug(request , slug)
        skip = page*rows
        orgSize = getOrgSize(org)

        team = get_object_or_404(Team , id=id)
        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeader = isLeaderOrCoLeader(team , org , userData)
        if( not ( isHeOwner | isHeLeaderOrCoLeader)):
            return HttpResponseNotAllowed("You don't an access")
        
        avgAtt = getTeamAvgAttendance( request , slug , id , org._id )
        teamInsight = getTeamInsights( request , slug , id , org._id )
        print("teamInsight")
        print(teamInsight)
        print(avgAtt)

        teamsMembersDetails = TeamMember.objects.filter(Q(OrganizationId = org) & Q(TeamId = id) &                                 
         (Q(role__icontains=search) |
        Q(createdAt__icontains=search) |
        Q(userId__firstName__icontains=search) |
        Q(userId__middleName__icontains=search) |
        Q(userId__lastName__icontains=search) |
        Q(createdBy__firstName__icontains=search) |
        Q(createdBy__middleName__icontains=search) |
        Q(createdBy__lastName__icontains=search) |
        Q(userId__email__icontains=search) |
        Q(userId__address__city__icontains=search) |
        Q(userId__address__state__icontains=search) |
        Q(userId__address__country__icontains=search) |
        Q(userId__address__code__icontains=search))
        ).order_by("-createdAt")
        
        tableTitle , tableData = getTeamsMemebesFormatedData(teamsMembersDetails,id , org)
        openAction = False
        editAction = True
        deleteAction = True
        addAction = True
        navOptions = {
            "leave_request" : isHeLeaderOrCoLeader | isHeOwner,
            'job_title' : isHeOwner,
            'teams' : isHeLeaderOrCoLeader | isHeOwner,
            'employees' : isHeOwner
        }
        print(tableTitle )
        print(tableData)

        today = datetime.today()
        year = today.year
        print("===============year========================")

        if (request.method == "POST" and request.POST["year"] is not None):
            print("request.POST['year'']")
            print(request.POST["year"])
            year = int(request.POST["year"])

        attendanceDataOfTeam = getAttendance(request , slug , teamId=id ,year=year)

        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"TeamDetails.html" , { 
            "slug" : slug ,
            "org": org ,
            "user" : user,
            "orgSize":orgSize,
            "takeAttendance" : True,
            "teamId" : id,
            "afterSlug":f"{id}",
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"organization",
            "page" : "team-details" ,
            "teamName": team.name,
            "teamsMembersDetails" : teamsMembersDetails[ skip :  skip + rows],
            "totalMemeberTeams" : np.arange(0, math.ceil(len(teamsMembersDetails)/10)),
            "AvgAttendance" : avgAtt,
            "checkInTime" : teamInsight.get("checkInTime" , 0),
            "checkOutTime" : teamInsight.get("checkOutTime" , 0),
            "leaderCount" : teamInsight.get("leaderCount" , 0),
            "coLeaderCount" : teamInsight.get("coLeaderCount" , 0),
            "memberCount" : teamInsight.get("memberCount" , 0),
            "totalParticipantsCount" : teamInsight.get("totalParticipantsCount" , 0),
            'tableTitle':tableTitle,
            'navOptions' :navOptions,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "deleteAction":deleteAction,
            "addAction":addAction,
            "columnCount":6,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search,
            "att_data" : attendanceDataOfTeam,
            "year" : year,
            "isOwner" : isHeOwner
             })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def addTeamMember(request , slug ,teamId):
    try:
        print("==============================================")
        print("addTeamMember")
        print(slug , teamId)
        user = request.session["user"]

        userData = get_object_or_404(Users , _id = user["_id"])
        org = Organization.objects.get(_id = user["currentActiveOrganization"])

        team = get_object_or_404(Team , id = teamId ,OrganizationId = org )
        print(team)
        print(request.method)

        isHeOwner = isOwner(org , userData)
        if( not ( isHeOwner | isLeaderOrCoLeader(team , org , userData))):
            return HttpResponseNotAllowed("You don't an access")

        if(request.method == "POST"):
            print("post")
            form = addEmployeeToTeam(request.POST)
            if form.is_valid():
                print(form.is_valid())
                data = request.POST
                print("request data")
                print(data)
                print(request.POST["Position"] , )
                u = getUserByEmail(request.POST["email"])
                print(u)
                saveTeamMemberData(request , u,form,request.POST["Position"],team,org,user)
                print("team")
                return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
            else:
                print("form invalid")
                return render(request ,"AddEmployeeToTeam.html", { 'form' : form , 'slug' : slug , 
                     'teamId':teamId,
                     'slug':slug,
                     'title' : f"Add new employee to {team.name}", 
                     })
        else:
            print("get request")
            form = addEmployeeToTeam()            
            return render(request ,"AddEmployeeToTeam.html", { 'form' : form , 'slug' : slug , 
                     'teamId':teamId,
                     'slug':slug,
                     'title' : f"Add new employee to {team.name}", 
                     })
    except Exception as e:
        return HttpResponseServerError(e)

def editTeamMember(request , slug ,teamId, id , employeeId):
    try:
        print("==============================================")
        print(slug , teamId, id , employeeId)
        user = request.session["user"]

        org = Organization.objects.get(_id = user["currentActiveOrganization"])

        emp = Employee.objects.get( _id = employeeId , Organization = org)
        team = Team.objects.get( id = teamId)
        print(team)

        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        if( not ( isHeOwner | isLeaderOrCoLeader(team ,org, userData))):
            return HttpResponseNotAllowed("You don't an access")

        if(request.method == "POST"):

            form = ChangeEmployeeRoleInTeam(request.POST, organization=org)
            if form.is_valid():
                role = request.POST["role"]
                Employee.objects.filter(_id = employeeId).update(jobTitle = Job_title.objects.get(Organization = org , title = role))

                position = request.POST["Position"]
                TeamMember.objects.filter(id = id).update(role = position)

                print(f"/organization/teams/{org.slug}/{teamId}")
                return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
            else:
                return render(request ,"ChangeEmployeeRoleInTeam.html", { 'form' : form ,'slug' : slug , 
                     'id' : id ,
                     'teamId':teamId,
                     'teamName' : team.name,
                     'employeeId' : employeeId })
        else:
            query_dict = QueryDict(mutable=True)
            teamMem = TeamMember.objects.filter(id = id , userId = emp.employee )
            print("---------")
            print(id , employeeId)
            print(teamMem)
            query_dict.appendlist("Position",teamMem[0].role)
            query_dict.appendlist("Name",f"{emp.employee.firstName} {emp.employee.middleName} {emp.employee.lastName}")
            query_dict.appendlist("role",emp.jobTitle.title)
            print(query_dict)
            form = ChangeEmployeeRoleInTeam( query_dict , organization=org)
            # print(form)
            
            return render(request ,"ChangeEmployeeRoleInTeam.html", { 'form' : form , 'slug' : slug , 
                     'id' : id ,
                     'teamId':teamId,
                     'teamName' : team.name,
                     'employeeId' : employeeId 
                     })
    except Exception as e:
        return HttpResponseServerError(e)

def deleteTeamMember(request , slug ,teamId, id , employeeId):
    try:
        user = request.session["user"]

        org = Organization.objects.get(_id = user["currentActiveOrganization"])

        emp = Employee.objects.get( _id = employeeId , Organization = org)

        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        if( not ( isHeOwner | isLeaderOrCoLeader(org , userData))):
            return HttpResponseNotAllowed("You don't an access")


        if(request.method == "POST"):
            TeamMember.objects.filter(id = id).delete()
            return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
        else:
            return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
    except Exception as e:
        return HttpResponseServerError(e)

def getTeamInsights(request , slug , teamId , orgId):
    try:
        queryToGetTeamMembersCountBasedOnRole = f"""
        SELECT 
                tm.id as id,
                sum(case WHEN role = "LEADER" then 1 else 0 END) as leaderCount,
                sum(case when role = "CO-LEADER" THEN 1 else 0 END) as coLeaderCount,
                sum(case when role = "MEMBER" THEN 1 else 0 END) as memberCount,
                count(*) as total,
                t.checkInTime,
                t.checkOutTime
                FROM Organization_teammember as tm,
                Organization_team as t

                WHERE 
                tm.id <> -1 AND
                t.OrganizationId_id = {orgId} AND
                TeamId_id = {teamId} AND
                t.OrganizationId_id = tm.OrganizationId_id AND
                t.id = tm.TeamId_id;
        """
        d1 = TeamMember.objects.raw(queryToGetTeamMembersCountBasedOnRole)

        checkInTime=0
        checkOutTime=0
        leaderCount = 0
        coLeaderCount = 0
        memberCount = 0
        totalParticipantsCount = 0

        print("team insight")
        print(d1)
        print(len(d1))

        for d in d1:
            print(d)
            checkInTime = d.checkInTime
            checkOutTime = d.checkOutTime
            leaderCount = d.leaderCount
            coLeaderCount = d.coLeaderCount
            memberCount = d.memberCount
            totalParticipantsCount = d.total

        return {
            "checkInTime" : checkInTime,
            "checkOutTime" : checkOutTime,
            "leaderCount" : leaderCount,
            "coLeaderCount" : coLeaderCount,
            "memberCount" : memberCount,
            "totalParticipantsCount" : totalParticipantsCount,
        }
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def getTeamAvgAttendance(request , slug , teamId , orgId):
    try:
        QueryBuilder = ""
        if(type(teamId).__name__ == 'int' or type(teamId).__name__ == 'str'):
            QueryBuilder = f" AND TeamId_id = {teamId} "
        
        elif( type(teamId).__name__ ==  "tuple"):
            teamId = list(teamId)
            if len(teamId) <= 1:
                teamId.append(-1)
                teamId.append(-1)
            QueryBuilder = f" AND TeamId_id in {tuple(teamId)} "
            
        print("getTeamAvgAttendance")
        queryToGetAttendanceOfTeam = f"""
                SELECT 
                id,
                sum(case when attendance = 1 then 1 else 0 end) as present,
                sum(case when attendance = 0 then 1 else 0 end) as absent,
                count(*) as total
                FROM Organization_attendance a
                WHERE 
                id <> -1 and
                Organization_id = {orgId} 
                {QueryBuilder}
                GROUP BY takenAt;
        """ 
        d2 = Attendance.objects.raw(queryToGetAttendanceOfTeam)

        Attendancedata = 0
        print(d2)
        print(f"length of d2 = {len(d2)}")
        for d in d2:
            print(d.present , d.total)
            if(d.present == 0 or d.total == 0):
                continue
            Attendancedata += d.present / d.total
            print(Attendancedata)

        if(len(d2) != 0):
            Attendancedata = round((Attendancedata / len(d2) ) * 100)


        return Attendancedata
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def getJobTitleFormatedData(jobTitleData):
    tableTitle = ["Job Title","Created By","Created At"]
    tableData = []
    for i in  range(0,len(jobTitleData)):
        jobs = jobTitleData[i]
        tableData.append([ 
            f'{jobs.title}' ,
            f'{jobs.createdBy.firstName} {jobs.createdBy.middleName} {jobs.createdBy.lastName}' ,
            f'{jobs.createdAt}',
            f'{jobs.id}',
        ])
    return tableTitle , tableData

def jobTitle(request , slug):
    try:
        search=""
        rows=10
        page=0
        data = request.POST
        print(data)
        user = request.session["user"]


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"])
        

        print("data ===>")
        print(search , rows)

        org = getOrgBySlug(request , slug)
        skip = page*rows
        orgSize = getOrgSize(org)
        JobTitleData = Job_title.objects.filter(Q(Organization = org) &
         (Q(title__icontains=search) |
          Q(createdBy__firstName__icontains=search) |
          Q(createdBy__middleName__icontains=search) |
          Q(createdBy__lastName__icontains=search)
          )).order_by("-createdAt")
        
        tableTitle , tableData = getJobTitleFormatedData(JobTitleData)
        print(tableTitle)
        print(tableData)

        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        if( not ( isHeOwner )):
            return HttpResponseNotAllowed("You don't an access")


        openAction = isHeOwner
        editAction = isHeOwner
        deleteAction = isHeOwner
        addAction = isHeOwner
        navOptions = {
            "leave_request" : isHeOwner,
            'job_title' : isHeOwner,
            'teams' : isHeOwner,
            'employees' : isHeOwner
        }

        data = { 
            "slug" : slug ,
            "org": org ,
            "user" : user,
            "orgSize":orgSize,
            "afterSlug":"add",
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND') ,
            "endpoint":"organization",
            "page" : "job-title",
            # "JobTitleData" : tableData
            "totalJobTitle" : np.arange(0, math.ceil(len(JobTitleData)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "columnCount" : 4,
            "openAction" : openAction,
            "editAction" : editAction,
            "deleteAction" : deleteAction,
            "navOptions" : navOptions,
            "addAction" : addAction,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search ,
            "isStatsToShow":True,
            "isOwner" : isHeOwner
             }
        print(data)
        return render(request ,"JobTitle.html" , data)
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def jobTitleDetails(request , slug ,jobTitleId):
    try:
        user = request.session["user"]
        search=""
        rows=10
        page=0
        data = request.POST
        print("======================================================")
        print(jobTitleId)
        print(data)

        org = getOrgBySlug(request , slug)

        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        if( not ( isHeOwner )):
            return HttpResponseNotAllowed("You don't an access")


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"])
        

        print("data ===>")
        print(search , rows)

        jobTitle= get_object_or_404(Job_title , id=jobTitleId)
        skip = page*rows
        orgSize = getOrgSize(org) 
        employeeData = Employee.objects.filter(Q(Organization = org) & Q(jobTitle = jobTitle) &
         (Q(jobTitle__title__icontains=search) |
          Q(employee__firstName__icontains=search) |
          Q(employee__middleName__icontains=search) |
          Q(employee__lastName__icontains=search) |
          Q(employee__email__icontains=search) |
          Q(employee__DOB__icontains=search) |
          Q(employee__phoneNumber__icontains=search) |
          Q(employee__address__city__icontains=search) |
          Q(employee__address__state__icontains=search) |
          Q(employee__address__country__icontains=search) |
          Q(employee__address__code__icontains=search) |
          Q(createdBy__firstName__icontains=search) |
          Q(createdBy__middleName__icontains=search) |
          Q(createdBy__lastName__icontains=search) |
          Q(createdBy__email__icontains=search) |
          Q(createdBy__address__city__icontains=search) |
          Q(createdBy__address__state__icontains=search) |
          Q(createdBy__address__country__icontains=search) |
          Q(createdBy__address__code__icontains=search)
          )).order_by("-createdAt")
        
        tableTitle , tableData = getEmployeeFormatedData(employeeData , jobTitleId=jobTitleId)
        print(tableTitle)
        print(tableData)

        openAction = False
        editAction = True
        deleteAction = True
        addAction = True

        navOptions = {
            "leave_request" :  isHeOwner,
            'job_title' : isHeOwner,
            'teams' : isHeOwner,
            'employees' : isHeOwner
        }

        data = { 
            "slug" : slug ,
            "org": org ,
            "user" : user,
            "orgSize":orgSize,
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND') ,
            "endpoint":"organization",
            "page" : "job-title",
            'jobTitleDetails':True,
            'jobTitleId':jobTitleId,
            'afterSlug': f'add/{jobTitleId}',
            # "JobTitleData" : tableData
            "totalJobTitle" : np.arange(0, math.ceil(len(employeeData)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "columnCount" : 8,
            "openAction" : openAction,
            "editAction" : editAction,
            "deleteAction" : deleteAction,
            "addAction" : addAction,
            "navOptions":navOptions,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search ,
            "isStatsToShow":False,
            "jobTitle" : jobTitle.title,
            "isOwner" : isHeOwner
             }
        print(data)
        return render(request ,"JobTitle.html" , data)
    except Exception as e:
        print(e)
        return HttpResponseServerError()

def getEmployeeFormatedData(employeeData , jobTitleId=""):
    tableTitle = ["Name","Job Title","Email","DOB","Phone Number","Address","createdAt"]
    tableData = []
    if jobTitleId != "":
        jobTitleId += "/"

    for i in  range(0,len(employeeData)):
        emp = employeeData[i]
        address = "-"
        DOB = "-"
        phoneNumber = "-"
        if emp.employee.DOB != None :
            DOB = emp.employee.DOB

        if emp.employee.phoneNumber != None :
            phoneNumber = emp.employee.phoneNumber

        if emp.employee.address :
            address = f'{emp.employee.address.city} {emp.employee.address.state} {emp.employee.address.country} {emp.employee.address.code}'

        tableData.append([ 
            f'{emp.employee.firstName} {emp.employee.middleName} {emp.employee.lastName}' ,
            f'{emp.jobTitle.title}',
            f'{emp.employee.email}',
            f'{DOB}',
            f'{phoneNumber}',
            address,
            f'{emp.createdAt}',
            f'{jobTitleId}{emp._id}',
        ])
    return tableTitle , tableData

def employees(request , slug):
    try:
        user = request.session["user"]
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
        

        print("data ===>")
        print(search , rows)

        org = getOrgBySlug(request , slug)
        skip = page*rows
        orgSize = getOrgSize(org)
        userData = get_object_or_404(Users , _id = user["_id"])

        isHeOwner = isOwner(org , userData)
        print(isHeOwner)
        if( not ( isHeOwner | isLeaderOrCoLeaderInAtleastOneTeam(org , userData))):
            return HttpResponseNotAllowed("You don't an access")

            # Q(employee = userData)
        userList = getAllUserIdListOfOrgForUser(org , userData)
            # &
            # Q(employee__in = userList)
        co_Leader = 0
        leader = 0
        member = 0
        total = 0
        avgAtt = 0

        if isHeOwner:
            co_Leader,leader,member,total = roleCountOfTeamsOrOrg(org_id= org._id , teamIds=False)
            avgAtt = getTeamAvgAttendance(request , slug , teamId=False , orgId=org._id)
        else:
            teamIds = getTeamIdList(org , userData)
            if len(teamIds) <= 1:
                teamIds.append(-1)
                teamIds.append(-1)
            co_Leader,leader,member,total = roleCountOfTeamsOrOrg(org_id= org._id , teamIds=tuple(teamIds))
            avgAtt = getTeamAvgAttendance(request , slug , tuple(teamIds) , org._id)

        employeeData = Employee.objects.filter(
            Q(Organization = org) 
            &
         (Q(employee__DOB__icontains=search) |
            Q(employee__phoneNumber__icontains=search) |
            Q(employee__firstName__icontains=search) |
            Q(employee__middleName__icontains=search) |
            Q(employee__lastName__icontains=search) |
            Q(jobTitle__title__icontains=search) |
            Q(employee__email__icontains=search) |
            Q(employee__address__city__icontains=search) |
            Q(employee__address__state__icontains=search) |
            Q(employee__address__country__icontains=search) |
            Q(employee__address__code__icontains=search))
            ).order_by("-createdAt")
        
        tableTitle , tableData = getEmployeeFormatedData(employeeData)
        openAction = False
        editAction = isHeOwner
        deleteAction = isHeOwner
        addAction = isHeOwner

        navOptions = {
            "leave_request" : isHeOwner,
            'job_title' : isHeOwner,
            'teams' : isHeOwner,
            'employees' : isHeOwner
        }
        print(employeeData )
        print(len(employeeData))

        return render(request ,"Employee.html" , { 
            "slug" : slug , 
            "org": org ,
            "user" : user,
            "orgSize":orgSize,
            "afterSlug":"add",
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND') ,
            "endpoint":"organization",
            "page" : "employees" ,
            "co_Leader":co_Leader,
            "leader":leader,
            "member":member,
            "total":total,
            "avgAtt":avgAtt,
            "employeeData" : employeeData[ skip :  skip + rows],
            "totalEmployee" : np.arange(0, math.ceil(len(employeeData)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "addAction":addAction,
            "navOptions" :navOptions,
            "deleteAction":deleteAction,
            "columnCount" : 8,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search,
            "isOwner" : isHeOwner
             })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def saveEmployeeData(request , user, org , redirectUrl,action , isEdit = False):
    print("post method")
    print(request.POST)
    form = addEmployeeForm( request.POST, organization=org)
    if form.is_valid():
        userToAdd = Users.objects.filter(email = request.POST["email"])

        if(len(userToAdd) == 0):
            form.add_error("email" , "User with this email not found")
            return render(request ,"AddEmployee.html", { 'form' : form , 'action':action})
        
        print("userToAdd")
        print(userToAdd)

        role = Job_title.objects.get(id = request.POST["role"])
            
        try:
            employeeDetails = Employee.objects.filter(
                        Q(employee = userToAdd[0]),
                        Q(Organization = org),
                        # Q(jobTitle = role)
            )

            if len(employeeDetails) > 0:
                form.add_error("email" , "Same Employee with this role is already exist")
                return render(request ,"AddEmployee.html", { 'form' : form , 'action':action})

            print("employeeDetails")
            print(employeeDetails)

        except Employee.DoesNotExist:
            return HttpResponseServerError("Employee not found")


        if not isEdit:
            emp = Employee(
                employee = userToAdd[0] , 
                jobTitle = role,
                createdBy = Users.objects.get(_id = user["_id"]),
                Organization = org
                )
            emp.save()
            return HttpResponseRedirect(redirectUrl)
        else:
            Employee.objects.filter()
    else:
        return render(request ,"AddEmployee.html", { 'form' : form })

def AddEmployee(request , slug):
    try:
        print("entered add employee")
        user = request.session["user"]
        print(user)
        org = Organization.objects.get(_id = user["currentActiveOrganization"])
        print(org)
        userData = get_object_or_404(Users, _id = user["_id"])

        if not isOwner(org , userData):
            return HttpResponseNotAllowed()
        
        if(request.method == "POST"):
            return saveEmployeeData(request,user,org,f"/organization/employees/{org.slug}",f"/organization/employees/{slug}/add")
        else:
            form = addEmployeeForm(organization=org)
            return render(request ,"AddEmployee.html", { 'form' : form , 'action':f"/organization/employees/{slug}/add"})
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def deleteEmployee(request ,slug , id):
    try:
        user = request.session["user"]
        print("delete employee")
        print(user)
        org = getOrgBySlug(request,slug)
        emp = get_object_or_404(Employee , _id = id )
        userData = get_object_or_404(Users, _id = user["_id"])

        if( not isOwner(org , userData)):
            return HttpResponseNotAllowed("You don't an access")
        
        if request.method == "POST":
            Employee.objects.filter( 
                    _id = id,      
                    Organization = org
            ).delete()
            return HttpResponseRedirect(f"/organization/employees/{org.slug}")
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)

def editEmployee(request, slug , id):
    try:
        user = request.session["user"]
        print("edit employee")
        print(user)
        org = getOrgBySlug(request,slug)
        emp = get_object_or_404(Employee , _id = id )
        userData = get_object_or_404(Users, _id = user["_id"])

        print(userData)
        print(emp.employee.email)

        if( not isOwner(org , userData)):
            return HttpResponseNotAllowed("You don't an access")

        if(request.method == "POST"):
            print("request.POST")
            print(request.POST)
            form = editEmployeeForm(request.POST["role"] , organization=org)

            if form.is_valid:
                print("valid ")
                newJob = get_object_or_404(Job_title , id=request.POST["role"])
                print(type(emp))
                print(userData)
                print(org)
                print(newJob)
                Employee.objects.filter( 
                    employee = userData,
                    Organization = org
                 ).update(jobTitle = newJob)
                
                return HttpResponseRedirect(f"/organization/employees/{org.slug}")
            else:
                return render(request ,"AddEmployee.html", { 'form' : form ,'action' : f"/organization/employees/{org.slug}/edit/{id}" , "isEdit" : True })
            # return saveEmployeeData(request,user,org,f"/organization/job-title/{org.slug}/{jobTitleId}" , f"/organization/job-title/{org.slug}/add/{jobTitleId}" , True)
        else:    
            q = QueryDict(mutable=True)
            q.appendlist("email" , emp.employee.email)
            q.appendlist("role" , emp.jobTitle.id)
            form = editEmployeeForm(q,organization=org)
            return render(request ,"AddEmployee.html", { 'form' : form ,'action' : f"/organization/employees/{org.slug}/edit/{id}" , "isEdit" : True })
    except Exception as e:
        return HttpResponseServerError(e)

def editEmployeeViaJobTitle(request, slug , jobTitleId , employeeId):
    try:
        user = request.session["user"]
        print("edit employee")
        print(user)
        org = getOrgBySlug(request,slug)
        job = get_object_or_404(Job_title , id=jobTitleId)
        print(job)
        emp = get_object_or_404(Employee , _id = employeeId ,jobTitle = job )
        userData = get_object_or_404(Users, _id = emp.employee._id)

        print(userData)
        print(emp.employee.email)

        if(request.method == "POST"):
            print("request.POST")
            print(request.POST)
            form = editEmployeeForm(request.POST["role"] , organization=org)

            if form.is_valid:
                print("valid ")
                newJob = get_object_or_404(Job_title , id=request.POST["role"])
                print(job)
                print(type(emp))
                print(userData)
                print(org)
                print(newJob)
                Employee.objects.filter( 
                    employee = userData,
                    Organization = org,
                    jobTitle = job,
                 ).update(jobTitle = newJob)
                
                return HttpResponseRedirect(f"/organization/job-title/{org.slug}")
            else:
                return render(request ,"AddEmployee.html", { 'form' : form ,'action' : f"/organization/job-title/{org.slug}/edit/{jobTitleId}/{employeeId}" , "isEdit" : True })
            # return saveEmployeeData(request,user,org,f"/organization/job-title/{org.slug}/{jobTitleId}" , f"/organization/job-title/{org.slug}/add/{jobTitleId}" , True)
        else:    
            q = QueryDict(mutable=True)
            q.appendlist("email" , emp.employee.email)
            q.appendlist("role" , job.id)
            form = editEmployeeForm(q,organization=org)
            return render(request ,"AddEmployee.html", { 'form' : form ,'action' : f"/organization/job-title/{org.slug}/edit/{jobTitleId}/{employeeId}" , "isEdit" : True })
    except Exception as e:
        return HttpResponseServerError(e)

def addEmployeeViaJobDetails(request , slug , jobTitleId ):
    try:
        user = request.session["user"]
        print("addEmployeeViaJobDetails")
        print(user)
        org = getOrgBySlug(request,slug)
        if(request.method == "POST"):
            return saveEmployeeData(request,user,org,f"/organization/job-title/{org.slug}/{jobTitleId}" , f"/organization/job-title/{org.slug}/add/{jobTitleId}")
        else:
            form = addEmployeeForm(organization=org)
            return render(request ,"AddEmployee.html", { 'form' : form ,'action' : f"/organization/job-title/{org.slug}/add/{jobTitleId}"})
    except Exception as e:
        return HttpResponseServerError(e)

def AddJobTitle(request ,slug):
    try:
        print("entered add job title")
        user = request.session["user"]
        print(user)
        org = getOrgBySlug(request , slug)
        print(org)
        if(request.method == "POST"):
            form = addJobTitleForm( request.POST)
            print("post method")
            print(request.POST)
            if form.is_valid():

                isDuplicate = Job_title.objects.filter(title = request.POST["title"] , Organization = org)

                if(len(isDuplicate) >= 1):
                    return HttpResponseNotAllowed(f"Duplicate job title")
                
                newJobTitle = Job_title(
                    title = request.POST["title"] ,
                    Organization = org,
                    createdBy = Users.objects.get(_id = user["_id"])
                    )
                newJobTitle.save()
                return HttpResponseRedirect(f"/organization/job-title/{org.slug}")
            else:
                return render(request ,"AddJobTitle.html", { 'form' : form })
        else:
            form = addJobTitleForm()
            return render(request ,"AddJobTitle.html", { 'form' : form , 'slug' : slug })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def EditJobTitle(request ,slug , id):
    try:
        print("entered edit job title")
        user = request.session["user"]
        print(user)
        org = getOrgBySlug(request , slug)
        jobTitle = get_object_or_404(Job_title , id=id)
        print(org)
        if(request.method == "POST"):
            form = addJobTitleForm( request.POST)
            print("post method")
            print(request.POST)
            if form.is_valid():

                isDuplicate = Job_title.objects.filter(title = request.POST["title"] , Organization = org)

                if(len(isDuplicate) >= 1):
                    return HttpResponseNotAllowed(f"Duplicate job title")
                
                Job_title.objects.filter(id=id).update(title = request.POST["title"])
                return HttpResponseRedirect(f"/organization/job-title/{org.slug}")
            else:
                return render(request ,"AddJobTitle.html", { 'form' : form })
        else:
            q = QueryDict(mutable=True)
            q.appendlist("title" , jobTitle.title)
            form = addJobTitleForm(q)
            return render(request ,"AddJobTitle.html", { 'form' : form , 'slug' : slug , 'isEdit' : True , 'jobTitleId' : id})
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)
    
def DeleteJobTitle(request , slug , id):
    try:
        if request.method == "POST":
            user = request.session["user"]
            print(user)
            org = getOrgBySlug(request , slug)
            get_object_or_404(Job_title , id=id).delete()
            return HttpResponseRedirect(f"/organization/job-title/{org.slug}")
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)
    
def AddLeaveRequest(request):
    try:
        currentUser = request.session["user"]
        org = get_object_or_404( Organization, _id = currentUser["currentActiveOrganization"])
        createdBy = get_object_or_404(Users ,_id = currentUser["_id"])
        print("Add leave request")
        if request.method == "POST":
            print(request.POST)
            form  = LeaveRequestForm(request.POST ,organization = org ,user = createdBy )
            if( request.POST["From"] < date.today().strftime('%Y-%m-%d') or request.POST["From"] > request.POST["To"]):
                form.add_error("From" , "Invalid from date")
            
            if not form.is_valid():
                return render(request , "AddLeaveRequest.html" , {
                        'form' : form
                        })
            
            else:
                 leaveType = request.POST["LeaveType"]
                 fromDate = request.POST["From"]
                 toDate = request.POST["To"]
                 reason = request.POST["reason"]
                 team = get_object_or_404( Team , id= request.POST["team"])
                 leaveRequest = LeaveRequest(
                     leaveType = leaveType,
                     fromDate = fromDate,
                     toDate = toDate,
                     reason = reason,
                     Organization = org,
                     createdBy = createdBy,
                     TeamId = team
                 )
                 leaveRequest.save()
                 return HttpResponseRedirect(f"/users/leave-request/{currentUser['slug']}")
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)
    
def getOrgSize(org):
    try:
        owner = OwnerDetails.objects.filter(OrganizationId = org).values_list('userId_id', flat=True).distinct()
        print(owner)
        member = TeamMember.objects.filter(Q(OrganizationId = org) & ~Q(userId_id__in = owner)).values_list('userId_id', flat=True).distinct()
        print(member)
        return len(owner) + len(member)
    except Exception as e:
        return HttpResponseServerError(e)

def leaveRequest(request , slug):
    try:
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])

        org = None
        if user["currentActiveOrganization"] is None:
            userInOrg = TeamMember.objects.filter(userId = userData).first()
            userInOrgOwner = OwnerDetails.objects.filter(userId = userData).first()

            if userInOrg is not None:
                Users.objects.filter(_id = user["_id"]).update(currentActiveOrganization = userInOrg.OrganizationId)
                
            elif userInOrgOwner is not None:
                Users.objects.filter(_id = user["_id"]).update(currentActiveOrganization = userInOrgOwner.OrganizationId._id)
            else:
                return HttpResponseRedirect(f"/users")
            org = get_object_or_404( Organization, _id = userData.currentActiveOrganization)

        if org is None:
            org = get_object_or_404( Organization, _id = user["currentActiveOrganization"])

        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org , userData)
        if( not ( isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam)):
            return HttpResponseNotAllowed("You don't an access")
        print("leaveRequest")

        # for pagination
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
        
        skip = page*rows

        orgSize = getOrgSize(org)
        ownerOrgData = OwnerDetails.objects.filter(OrganizationId = org , userId = userData).values_list('OrganizationId', flat=True).distinct()        
        leaveReq = None
        print(ownerOrgData)
        if(len(ownerOrgData) >= 1):
            #    & Q(createdBy__id__not = userData._id)
            leaveReq = LeaveRequest.objects.filter(Q(Organization_id__in = ownerOrgData) 
                                                    &(
                Q(status__icontains=search) |
                Q(reason__icontains=search) |
                Q(leaveType__icontains=search) |
                Q(fromDate__icontains=search) |
                Q(createdBy__firstName__icontains=search) |
                Q(createdBy__middleName__icontains=search) |
                Q(createdBy__lastName__icontains=search) |
                Q(toDate__icontains=search) 
            )).order_by("-createdAt") 

        else:
            teamList = TeamMember.objects.filter( OrganizationId = org,  role__in = ["LEADER" , "CO-LEADER"] , userId = userData).values_list('TeamId',flat=True).distinct()
            leaveReq = LeaveRequest.objects.filter(Q(TeamId__id__in =teamList)  &(
                    Q(status__icontains=search) |
                    Q(reason__icontains=search) |
                    Q(leaveType__icontains=search) |
                    Q(fromDate__icontains=search) |
                    Q(toDate__icontains=search) 
                )).order_by("-createdAt") 

        if leaveReq == None:
            return HttpResponseNotAllowed()
        
        
        # only (leader or co-leader) of a team or owner of that org.. can view
        
        openAction = True
        editAction = False
        deleteAction = True
        addAction = False
        
        navOptions = {
            "leave_request" : isHeLeaderOrCoLeaderInAtleastOneTeam | isHeOwner,
            'job_title' : isHeOwner,
            'teams' : isHeLeaderOrCoLeaderInAtleastOneTeam | isHeOwner,
            'employees' : isHeOwner
        }

        print("leaveReq===>")
        print(leaveReq)
        tableTitle , tableData  = formateLeaveRequest(leaveReq)
        
        return render(request ,"LeaveRequest.html" , 
                    {
                "slug" : slug ,
                "user" : user,
                "navOptions" : navOptions,
                "org": org ,
                "page" : "leave-request" ,
                "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
                "orgSize" : orgSize,
                "endpoint":"organization",
                "baseUrl" : os.environ.get('FRONTEND'),
                "totalRequests" : np.arange(0, math.ceil(len(leaveReq)/10)),
                'tableTitle':tableTitle,
                'tableData':tableData[ skip :  skip + rows],
                "openAction":openAction,
                "editAction":editAction,
                "addAction":addAction,
                "deleteAction":deleteAction,
                "columnCount":7,
                "pageNo":page,
                "skip":skip,
                "rows":rows,
                "search":search,
                "isOwner" : isHeOwner
                    } 
                    )
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def LeaveRequestDetails(request , slug , id):
    try:
        currentUser = request.session["user"]
        org = get_object_or_404( Organization, _id = currentUser["currentActiveOrganization"])

        userData = get_object_or_404(Users , _id = currentUser["_id"])
        showChangeStatus = False
        leaveReq = get_object_or_404(LeaveRequest , id = id)

        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeader = isLeaderOrCoLeader(leaveReq.TeamId,org , userData)
        print(isHeOwner)
        print(isHeLeaderOrCoLeader)

        print("leaveReq.exists()")
        print(leaveReq)

        if( not ( isHeOwner or isHeLeaderOrCoLeader)):
            return HttpResponseNotAllowed("You don't an access")
        
        if (isHeLeaderOrCoLeader or isHeOwner) :
            showChangeStatus = True

        if leaveReq.createdBy == userData:
            showChangeStatus = False
        
        if leaveReq.fromDate < date.today():
            print("from date is smaller")
            showChangeStatus = False

        return render(request , "LeaveRequestDetails.html" , {
            'data' : leaveReq,
            "slug" : slug,
            'id' : id,
            'showChangeStatus' :showChangeStatus
        })
    except Exception as e:
        return HttpResponseServerError(e)
    
def editLeaveRequestStatus(request , slug , id):
    try:
        if request.method == "POST":
            status = request.POST["status"]
            currentUser = request.session["user"]
            userData = get_object_or_404(Users , _id = currentUser["_id"])
            print(userData)
            org = get_object_or_404( Organization, _id = currentUser["currentActiveOrganization"])
            print(org)

            leaveReq = get_object_or_404(LeaveRequest , id = id , Organization = org)

            if LeaveRequest.objects.filter( id = id , Organization = org , createdBy= userData).exists():
                return HttpResponseNotAllowed()
            
            isHeOwner = isOwner(org , userData)
            print(isHeOwner)
            if( not ( isHeOwner | isLeaderOrCoLeader(leaveReq.TeamId ,org , userData))):
                return HttpResponseNotAllowed("You don't an access")

            if leaveReq.fromDate < date.today():
                print("from date is smaller")
                return Http404()
                
            else:
                print("else")
                LeaveRequest.objects.filter(id = id , Organization = org ).update(status = status , verifiedBy = userData)
                return HttpResponseRedirect(f"/organization/leave-request/{slug}")
        else:
            return Http404()
    except Exception as e:
        return HttpResponseServerError(e)

def getAttendance(request , slug , teamId , year):
    try:
        print("getAttendance")
        print(year)
        DayInNumber = {
            'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6
        }

        att_data = {1 : {},2: {},3: {},4: {},5: {},6: {},7: {},8: {},9: {},10: {},11: {},12: {}}

            # a.TeamId_id as TeamId,
        fromDate = datetime(year, 1, 1).strftime("%Y-%m-%d")
        toDate = datetime(year+1, 1, 1) - timedelta(days=1)
        toDate = toDate.strftime("%Y-%m-%d")
        print(f"from => {fromDate} to => {toDate}")
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
            TeamId_id = {teamId} and
            takenAt between '{fromDate}' and '{toDate}'
        GROUP BY 
            takenAt ORDER BY takenAt;
        """

        print(query)
        data = Attendance.objects.raw(query)

        print(data)
        print("data")
        for d in data:
            print(d)
            # x = date(d.takenAt)
            print(f"date => {d.takenAt.day} month => {d.takenAt.month} year => {d.takenAt.year}")
            att_data[d.takenAt.month][d.takenAt.day] = {
                    'percentage' : math.ceil(d.present / d.total) * 100,
                    "validCell" : True , "noAttendance" : False,
                    "takenAt" : d.takenAt
            }

        print(att_data)
        
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

            print(f"Month: {i + 1}, Year: {year}")
            print(f"start day=> {start_day}, last Day => {last_day}")
            print(f"total div => {total_number_of_div}")

            defaultAttenance = { 'percentage' : 0 , "validCell" : False , "noAttendance" : False}
            # print("=============================")
            # print(DayInNumber[start_day])
            # print(total_number_of_div -(6 - DayInNumber[last_day]))
            # print("=============================")
            day = 1;
            for j in range(total_number_of_div):
                if (j >= DayInNumber[start_day] and j < (total_number_of_div -(6 - DayInNumber[last_day]))):
                    finalCalendarData[str(i+1)][str(j)] = att_data[i+1].get(day , { 'percentage' : 0 ,  "validCell" : True , "noAttendance" : True })
                    day = day +1
                else:
                    finalCalendarData[str(i+1)][str(j)] = defaultAttenance
        print("finalCalendarData.items()")
        for i in range(1,13):
            print("i => ",i)
            print(len(finalCalendarData[f"{i}"]))
        return finalCalendarData
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def getAttendanceBasicDetails(request , org , team , teamId):
    try:
        team_data = {
            "orgName" : org.name,
            "teamTitle" : team.name,
            "checkInTime" : team.checkInTime,
            "OrganizationId" : team.OrganizationId,
            "checkOutTime" : team.checkOutTime,
            "description" : team.description,
        }
        query = f"""
                SELECT
                    tm.*,
                    a.*,
                    COUNT(a.id) AS total_days,
                    SUM(CASE WHEN a.attendance = 1 THEN 1 ELSE 0 END) AS days_present,
                    SUM(CASE WHEN a.attendance = 0 THEN 1 ELSE 0 END) AS days_absent
                FROM
                    Organization_teammember tm
                LEFT JOIN
                    Users_users AS u ON tm.userId_id = u._id
                LEFT JOIN
                    Organization_attendance AS a ON a.userId_id = u._id AND a.TeamId_id = tm.TeamId_id
                WHERE
                    tm.TeamId_id = {teamId}
                GROUP BY
                    tm.userId_id
                ORDER BY
                    u.firstName, u.middleName, u.lastName;
        """
        print(query)
        data = Attendance.objects.raw(query)
        att_data = []
        for d in data: 
            percentage = 0
            if(d.days_present != 0 and d.total_days != 0):
                percentage = math.ceil((d.days_present / d.total_days) * 100)
            user = {
                'userId' : d.userId._id,
                'logo' : f"{os.environ.get('FRONTEND')}/media/{d.userId.logo}",
                'name' : f"{d.userId.firstName} {d.userId.middleName} {d.userId.lastName}",
                'percentage' : percentage
            }
            att_data.append(user)
        print(att_data)
        return att_data , team_data
    except Exception as e:
        return HttpResponseServerError(e)

def takeAttendance(request , slug , teamId):
    try:
        user = request.session["user"]
        org = getOrgBySlug(request,slug)
        team = get_object_or_404(Team , id = teamId)
        userData = get_object_or_404(Users , _id = user["_id"])

        att_data , team_data = getAttendanceBasicDetails(request , org , team , teamId)

        return render(request , "Attendance.html", {
            "att_data" : att_data,
            "slug" : slug,
            "teamId" : teamId,
            "team_data" : team_data
        })
    except Exception as e:
        return HttpResponseServerError(e)

def saveAttendance(request , slug , teamId):
    try:
        if request.method == "POST":
            user = request.session["user"]
            userData = get_object_or_404(Users , _id = user["_id"])
            data = request.POST
            org = getOrgBySlug(request,slug)
            team = get_object_or_404(Team , id = teamId)
            teamMembers = TeamMember.objects.filter(
                TeamId = team,
                OrganizationId = org
            )
            print("=============================================")
            print("request.POST['date']")
            date = request.POST["date"]

            isAttAllreadyTaken = Attendance.objects.filter(
                TeamId = team,
                Organization = org,
                takenAt = datetime.strptime(date, '%Y-%m-%d').date()
            )

            if(len(isAttAllreadyTaken) > 0):
                return HttpResponseServerError("Attendance for this date is already taken")

            for teamMem in teamMembers:
                isPresent = False
                if(data.get(f'{teamMem.userId._id}') == 'on'):
                    query = f"""
                        SELECT fromDate , toDate , status , createdBy_id , id
                        FROM 
                            Organization_leaverequest 
                        where 
                            Organization_id = {org._id}  AND
                            createdBy_id = {teamMem.userId._id} AND
                            status= "ACCEPTED" AND
                            '{datetime.strptime(date, '%Y-%m-%d').date()}' BETWEEN fromDate AND toDate;
                    """
                    data1 = LeaveRequest.objects.raw(query)

                    if(data1 is not None and len(data1) == 0):
                        isPresent = True
                
                att = Attendance(
                    attendance = isPresent,
                    TeamId = team,
                    Organization = org, 
                    createdBy = userData,
                    userId = teamMem.userId,
                    takenAt = datetime.strptime(date, '%Y-%m-%d').date()
                )
                att.save()
            return HttpResponseRedirect(f"/organization/teams/{slug}/{teamId}")
    except Exception as e:
        return HttpResponseServerError(e)
    

def getAttendanceDetails(request , slug , teamId , takenAt):
    try:
        takenDate = parser.parse(takenAt).date()
        print(takenDate)
        # takenDate = datetime.strptime(takenDate, '%Y-%m-%d').date()
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        org = getOrgBySlug(request,slug)
        team = get_object_or_404(Team , id = teamId)
        
        isHeLeaderOrCoLeader = isLeaderOrCoLeader(team , org , userData)
        isHeOwner = isOwner(org, userData)

        if(not (isHeOwner or isHeLeaderOrCoLeader)):
            return HttpResponseNotAllowed("You don't have an access.")
        
        team_data = {
            "orgName" : org.name,
            "teamTitle" : team.name,
            "checkInTime" : team.checkInTime,
            "OrganizationId" : team.OrganizationId,
            "checkOutTime" : team.checkOutTime,
            "description" : team.description,
        }
        teamInsights = getTeamInsights(request , slug , teamId , org._id)
        
        att_data = Attendance.objects.filter(Organization = org , takenAt = takenDate)
        query = f"""
                        SELECT 
                            count(*) as total,
                            count(LeaveType) as count,
                            LeaveType,
                            id
                        FROM 
                            Organization_leaverequest 
                        where 
                            Organization_id = {org._id}  AND
                            TeamId_id = {teamId} AND
                            status = "ACCEPTED" AND
                            '{takenDate}' BETWEEN fromDate AND toDate
                        GROUP BY status;
                    """
        data = LeaveRequest.objects.raw(query)

        print(data)

        leaveStats = {
            "total" : 0,
            'Sick Leave' : 0,
            'Casual Leave' : 0,
            'Privilege Leave' : 0,
            'Maternity Leave' : 0,
        }

        for d in data:
            leaveStats[f"{d.leaveType}"] = d.count
            leaveStats["total"] = d.total

        leaveStats["SickLeavePercentage"] = round(((leaveStats["Sick Leave"] / leaveStats["total"] * 100)) if leaveStats["total"] > 0 else leaveStats["total"])
        leaveStats["CasualLeavePercentage"] = round(((leaveStats["Casual Leave"] / leaveStats["total"] * 100)) if leaveStats["total"] > 0 else leaveStats["total"])
        leaveStats["PrivilegeLeavePercentage"] = round(((leaveStats["Privilege Leave"] / leaveStats["total"] * 100)) if leaveStats["total"] > 0 else leaveStats["total"])
        leaveStats["MaternityLeavePercentage"] = round(((leaveStats["Maternity Leave"] / leaveStats["total"] * 100)) if leaveStats["total"] > 0 else leaveStats["total"])
        leaveStats["SickLeave"] = leaveStats["Sick Leave"]
        leaveStats["CasualLeave"] = leaveStats["Casual Leave"]
        leaveStats["PrivilegeLeave"] = leaveStats["Privilege Leave"]
        leaveStats["MaternityLeave"] = leaveStats["Maternity Leave"]
        
        total = 0
        present = 0
        percentage = 0

        for d in att_data:
            total+=1
            if(d.attendance == 1):
                present+=1

        if(total != 0):
            percentage = round(((present / total) * 100))
        return render(request , "AttendanceDetails.html", {
            "att_data" : att_data,
            "slug" : slug,
            "teamId" : teamId,
            "team_data" : team_data,
            "teamInsights":teamInsights,
            "attendance_percentage" : percentage,
            "total" : total,
            "presentCount" : present,
            "absentCount" : total - present,
            "leaveStats":leaveStats,
            "date" : takenDate
        })
    except Exception as e:
        return HttpResponseServerError(e)
def getEmployeePerJobTitle(request , slug , fromDate , toDate):
    try:
        user = request.session["user"]
        org = getOrgBySlug(request,slug)
        userData = get_object_or_404(Users , _id = user["_id"])

        isHeOwner = isOwner(org , userData)

        if(not isHeOwner):
            return HttpResponseNotAllowed("You don't have any access")
        
        fromDate = fromDate.split("T")[0]
        toDate = toDate.split("T")[0]
        
        query = f"""
                SELECT 
                    jt.title as jobTitle,
                    count(e.employee_id) as total,
                    id
                FROM 
                    Organization_job_title as jt
                LEFT JOIN 
                    Organization_employee as e ON 
                    e.jobTitle_id = jt.id AND 
                    e.Organization_id = {org._id} AND
                    e.createdAt BETWEEN '{fromDate}' AND '{toDate}'
                WHERE
                        jt.Organization_id = {org._id}
                GROUP BY 
                    jt.title;
        """
        data = Job_title.objects.raw(query)

        label = []
        total = []

        for job in data:
            label.append(job.jobTitle)
            total.append(job.total)

        return JsonResponse(
            {
                "label" : label,
                "total" : total
            } 
        )
    except Exception as e:
        return HttpResponseServerError(e)
    
def getEmployeePerJobTitleByTeam(request , slug , teamId, fromDate , toDate):
    try:
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        
        org = getOrgBySlug( request , slug)
        
        team = get_object_or_404(Team , id = teamId)

        isHeOwner = isOwner(org , userData)
        print(isHeOwner)

        isHeLeaderOrCoLeader = isLeaderOrCoLeader(org=org , team=team , user=userData)
        print(isHeLeaderOrCoLeader)

        if(not (isHeOwner | isHeLeaderOrCoLeader)):
            return HttpResponseNotAllowed("You don't have an access.")
        
        fromDate = fromDate.split("T")[0]
        toDate = toDate.split("T")[0]
        
        query = f"""
                SELECT
                    jt.title as jobTitle,
                    count(e.employee_id) as total,
                    jt.id
                FROM
                    Organization_job_title as jt,
                    Organization_teammember as tm
                LEFT JOIN
                    Organization_employee as e ON
                    e.jobTitle_id = jt.id AND
                    e.Organization_id = {org._id} AND
                    jt.Organization_id = e.Organization_id AND
                    e.employee_id = tm.userId_id AND
                    tm.TeamId_id = {teamId} AND
                    e.createdAt BETWEEN '{fromDate}' AND '{toDate}'
                WHERE
                        jt.Organization_id = {org._id} 
                GROUP BY
                    jt.title;
        """
        data = Job_title.objects.raw(query)

        label = []
        total = []
        print(data)

        for job in data:
            label.append(job.jobTitle)
            total.append(job.total)

        return JsonResponse(
            {
                "label" : label,
                "total" : total
            } 
        )

    except Exception as e:
        return HttpResponseServerError(e)

def getEmployeeCountByTeam(request , slug , fromDate , toDate):
    try:
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        
        org = getOrgBySlug( request , slug)

        isHeOwner = isOwner(org , userData)
        print(isHeOwner)

        isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org=org  , user=userData)
        
        print(isHeLeaderOrCoLeaderInAtleastOneTeam)

        if(not (isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam)):
            return HttpResponseNotAllowed("You don't have an access.")
        
        queryBuilder = ""

        if(not isHeOwner):
            teamIds = getTeamIdList(org , userData)
            if len(teamIds) <= 1:
                teamIds.append(-1)
                teamIds.append(-1)
            queryBuilder = f"  t.id in {tuple(teamIds)} AND "
        
        fromDate = fromDate.split("T")[0]
        toDate = toDate.split("T")[0]
        
        query = f"""
                SELECT
                    t.name as name,
                    count(tm.userId_id) as total,
                    tm.id
                FROM
                    Organization_teammember as tm,
                    Organization_team as t
                WHERE
                    tm.OrganizationId_id = {org._id}  AND
                    tm.OrganizationId_id = t.OrganizationId_id  AND
                    tm.TeamId_id = t.id AND
                    { queryBuilder }
                    tm.createdAt BETWEEN '{fromDate}' AND '{toDate}'
                GROUP BY
                    tm.TeamId_id;
        """
        data = Job_title.objects.raw(query)

        label = []
        total = []

        print(queryBuilder)
        print(data)

        for job in data:
            label.append(job.name)
            total.append(job.total)

        return JsonResponse(
            {
                "label" : label,
                "total" : total
            } 
        )

    except Exception as e:
        return HttpResponseServerError(e)


def editCompanyProfile(request , slug):
    try:
        print("editCompanyProfile")
        user = request.session["user"]
        userData = get_object_or_404(Users , _id = user["_id"])
        
        org = getOrgBySlug( request , slug)

        isHeOwner = isOwner(org , userData)
        print(isHeOwner)

        if(not isHeOwner):
            return HttpResponseNotAllowed("You don't have an access.")
        
        ownersDetails = OwnerDetails(OrganizationId = org)

        if(request.method == "POST"):
            form = createOrganizationForm(request.POST)
            if form.is_valid():
                print("valid")
                print("logo")
                logo = request.FILES.get('logo' , False)
                print("f name")

                name = request.POST["name"]
                webSiteLink = request.POST["webSiteLink"]
                socialMediaLink = request.POST["socialMediaLink"]
                contactEmail = request.POST["contactEmail"]
                ownersDetails = request.POST["ownersDetails"]
                description = request.POST["description"]

                city = request.POST["city"]
                state = request.POST["state"]
                country = request.POST["country"]
                code = request.POST["code"]

                print("org.address_id")
                print(org.address_id)

                if logo != False:
                    orgDataToUpdate = Organization.objects.get(_id = org._id)    
                    orgDataToUpdate.logo = logo
                    orgDataToUpdate.save()

                temp_owners = ownersDetails.split(",")
                owners=[user["email"]]
                for email in temp_owners:
                    owners.append(email)
                
                if len(owners) <= 1:
                    owners.append("")
    
                print("checking for user existence")
                for email in owners:
                    print(email)
                    try:
                        user = Users.objects.get(email = email.strip())
                        print(user)
                    except Users.DoesNotExist:
                        form.add_error("ownersDetails" ,f"user with this email ({email}) not exist")
                        return render(request ,"CreateOrganization.html", { 'form' : form , 'slug' : slug, 'isEdit' : True })    

                print("updating address")
                Address.objects.filter(id = org.address_id).update(city= city,state= state,country= country,code= code)
                print("updating org")
                Organization.objects.filter(_id = org._id).update(
                    name = name,
                    webSiteLink = webSiteLink,
                    socialMediaLink = socialMediaLink,
                    contactEmail = contactEmail,
                    description     = description,
                )

                print("updating owners")
                print(owners)
                for email in owners:
                        user = Users.objects.get(email = email.strip())
                        isOwnerAlreadyOwner = OwnerDetails.objects.filter(OrganizationId = org , userId = user)
                        print(len(isOwnerAlreadyOwner))
                        if(len(isOwnerAlreadyOwner) <= 0):
                            own = OwnerDetails(OrganizationId = org , userId = user)
                            print("saving")
                            own.save()
                            print("saved")

                # for removing owner not in list
                query2 = f"""
                        DELETE
                        FROM
                            Organization_ownerdetails as own
                        WHERE
                            own.OrganizationId_id = {org._id} AND
                            own.userId_id in (
                                SELECT DISTINCT(u._id) FROM
                                    Users_users as u
                                WHERE
                                    u.email not in {tuple(owners)}
                            );
"""
                deletedOwners = OwnerDetails.objects.raw(query2)

                if(deletedOwners != None):
                    try:
                        for i in deletedOwners:
                            print(i)
                    except Exception as exc:
                        print(exc)
                        
                print(deletedOwners)

                return HttpResponseRedirect(f"/organization/{slug}")
            else:
                return render(request ,"CreateOrganization.html" , { 
                    'form' : form , 
                    'slug' : slug,
                    'isEdit' : True
                })

        elif(request.method == "GET"):
            address = Address.objects.filter(id = org.address.id)
            query_dict = QueryDict(mutable=True)
            query_dict.appendlist("name", org.name)
            query_dict.appendlist("webSiteLink", org.webSiteLink)
            query_dict.appendlist("socialMediaLink", org.socialMediaLink)
            query_dict.appendlist("contactEmail", org.contactEmail)
            query_dict.appendlist("logo", org.logo)
            query_dict.appendlist("description", org.description)

            query_dict.appendlist("city" , address[0].city)
            query_dict.appendlist("state" , address[0].state)
            query_dict.appendlist("country" , address[0].country)
            query_dict.appendlist("code" , address[0].code)

            query = """
                    select
                        DISTINCT(u.email),
                        own.id
                    FROM
                        Organization_ownerdetails as own,
                        Users_users as u,
                        Organization_organization as org
                    WHERE
                        org._id = 2 AND
                        org._id = own.OrganizationId_id AND
                        u._id = own.userId_id;
            """

            ownerData = OwnerDetails.objects.raw(query)
            ownersEmail = ""

            for owner in ownerData:
                if ownersEmail == "":
                    ownersEmail = owner.email;
                else:
                    ownersEmail = f"{ownersEmail},{owner.email}"
            
            query_dict.appendlist("ownersDetails", ownersEmail)
            print("query_dict")
            print(query_dict)
            
            form = createOrganizationForm(query_dict)
            return render(request ,"CreateOrganization.html" , { 'form' : form , "slug" : slug , 'isEdit' : True})
    except IntegrityError as e:
        print(e)
        print(e.args)  # This will print the error message
        print(e.args[0])  # This will print the error message
        form = createOrganizationForm(request.POST, request.FILES)
        for arg in e.args:
            if "contactEmail" in arg and "UNIQUE constraint failed" in arg:
                form.add_error("contactEmail" , "This email is already exist")
            if "name" in arg and "UNIQUE constraint failed" in arg:
                form.add_error("name" , "Organization name is already exist")
        return render(request ,"CreateOrganization.html", { 'form' : form })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)