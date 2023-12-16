import math
import os
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
                owners = data["ownersDetails"]
                owners = owners.split(",")
    
                print("checking for user existence")
                for email in owners:
                    print(email)
                    try:
                        user = Users.objects.get(email = email)
                        print(user)
                    except Users.DoesNotExist:
                        form.add_error("ownersDetails" ,f"user with this email ({email}) not exist")
                        return render(request ,"CreateOrganization.html", { 'form' : form })
                    
                    address = Address(city = data["city"], state = data["state"], country = data["country"], code = data["code"])
                    print(address)
                    address.save()
        
                    org = Organization( 
                        name=data['name'],
                        address=address,
                        webSiteLink=data['webSiteLink'],
                        socialMediaLink=data['socialMediaLink'],
                        contactEmail=data['contactEmail'],
                        logo=request.FILES['logo'], 
                        description=data['description'],
                        )
                    org.save()
    
                    for email in owners:
                        user = Users.objects.get(email = email)
                        ownersDetails = OwnerDetails(OrganizationId = org , userId = user)
                        ownersDetails.save()
                    return render(request ,"CreateOrganization.html", { 'form' : form })
            return render(request ,"CreateOrganization.html", { 'form' : form })
        else:
            form = createOrganizationForm()
            return render(request ,"CreateOrganization.html", { 'form' : form })
    except():
        form = createOrganizationForm()
        return render(request ,"CreateOrganization.html", { 'form' : form })
    

def companyProfile(request , slug):
    try:
        print("called companyProfile")
        user = request.session["user"]
        org = Organization.objects.get(slug = slug)
        
        orgSize = getOrgSize(org)
        print(f"{os.environ.get('FRONTEND')}/media/{org.logo}")
        userData = get_object_or_404(Users , _id = user["_id"])
        isHeOwner = isOwner(org , userData)
        isHeLeaderOrCoLeaderInAtleastOneTeam = isLeaderOrCoLeaderInAtleastOneTeam(org , userData)
        navOptions = {
            "leave_request" : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
            'job_title' : isHeOwner ,
            'teams' : isHeOwner | isHeLeaderOrCoLeaderInAtleastOneTeam,
            'employees' : isHeOwner
        }
        return render(request ,"companyProfile.html" , 
            { 
                "slug" : slug ,
                "user" : user,
                "org": org ,
                "page" : "COMPANY_PROFILE" ,
                "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
                "orgSize" : orgSize,
                "endpoint":"organization",
                "navOptions":navOptions,
                "baseUrl" : os.environ.get('FRONTEND')
            }
        )
    except():
        return render(request ,"companyProfile.html")        

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

def createOrUpdate(request , user,slug , isEdit, teamId=""):
    try:
        isUserPermittedToAdd(request)
        print(request.POST)
        form = createTeamForm(request.POST)
        if form.is_valid():
            data = request.POST
            if data["checkInTime"] > data["checkOutTime"]:
                form.add_error("checkOutTime" ,"Invalid CheckInTime and CheckOutTime , time interval between these must be of minimum 45min")
                title = "Create Team"
                if isEdit:
                    title = "Edit Team"
                    
                return render(request ,"CreateTeam.html", { 'form' : form , "slug" :slug , teamId:teamId, 'title' : title})
            print(data)
            print(type(data))
            createdBy = Users.objects.get(_id = user["_id"])
            org_id = Organization.objects.get(_id = user["currentActiveOrganization"])

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
                
                createrData = Users.objects.filter(email = user["email"])
                saveTeamMemberData(request,createrData[0] , form , "LEADER" ,team , org_id,user)

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
            leaderData = Users.objects.filter(email = data["leader"])
            print(leaderData)
            if len(leaderData) == 1:
                saveTeamMemberData(request,leaderData[0] , form , "LEADER" ,team , org_id,user)

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
            "search":search
             })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def getTeamsMemebesFormatedData(TeamsMembersData , teamId):
    tableTitle = ["name","role","job-title","createdBy","createdAt"]
    tableData = []
    print(tableTitle)
    for i in  range(0,len(TeamsMembersData)):
        teamMember = TeamsMembersData[i]
        print(teamMembersDetails)

        emp = Employee.objects.filter(employee = teamMember.userId)

        tableData.append([ 
            f'{teamMember.userId.firstName} {teamMember.userId.middleName} {teamMember.userId.lastName}',
            f'{teamMember.role}',
            f'{emp[0].jobTitle.title}',
            f'{teamMember.createdBy.firstName} {teamMember.createdBy.middleName} {teamMember.createdBy.lastName}',
            f'{teamMember.createdAt}',
            f'{teamId}/{teamMember.id}/{emp[0]._id}',
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
        
        tableTitle , tableData = getTeamsMemebesFormatedData(teamsMembersDetails,id)
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
            "afterSlug":f"add/{id}",
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"organization",
            "page" : "team-details" ,
            "teamName": team.name,
            "teamsMembersDetails" : teamsMembersDetails[ skip :  skip + rows],
            "totalMemeberTeams" : np.arange(0, math.ceil(len(teamsMembersDetails)/10)),
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
            "year" : year
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
        if( not ( isHeOwner | isLeaderOrCoLeader(org , userData))):
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
            "search":search 
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
            "search":search 
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
        employeeData = Employee.objects.filter(
            Q(Organization = org) &
            Q(employee__in = userList)
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
            "search":search
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
            return saveEmployeeData(request,user,org,f"/organization/employee/{org.slug}",f"/organization/employees/{slug}/add")
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
                
                return HttpResponseRedirect(f"/organization/employee/{org.slug}")
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
                 return HttpResponseRedirect(f"/users/leave-request/{currentUser["slug"]}")
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
        addAction = True
        
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
                "search":search
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
                    "validCell" : True , "noAttendance" : False
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
        print(finalCalendarData["1"])
        return finalCalendarData
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def takeAttendance(request , slug , teamId):
    try:
        user = request.session["user"]
        org = getOrgBySlug(request,slug)
        team = get_object_or_404(Team , id = teamId)
        userData = get_object_or_404(Users , _id = user["_id"])

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
                'name' : f"{d.userId.firstName} {d.userId.middleName} {d.userId.lastName}",
                'percentage' : percentage
            }
            att_data.append(user)
        print(att_data)

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
            for teamMem in teamMembers:
                isPresent = False
                if(data.get(f'{teamMem.userId._id}') == 'on'):
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