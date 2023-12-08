import math
import os
from django.http import QueryDict
from django.http import HttpResponseServerError , HttpResponseNotAllowed, JsonResponse , Http404 , HttpResponseRedirect
from django.shortcuts import render , get_object_or_404
import requests
from Organization.forms import createOrganizationForm, createTeamForm , addEmployeeForm , addJobTitleForm , ChangeEmployeeRoleInTeam , addEmployeeToTeam
from Organization.models import Organization ,OwnerDetails , Team ,TeamMember , Employee , Job_title
from Users.models import Address, Users
from Users.views import getUserByEmail
from django.db.models import Q
from datetime import datetime
from django.db.models import Count
import numpy as np

def getOrgBySlug(request , slug):
    try:
        org = Organization.objects.get(slug = slug)
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
        owner = OwnerDetails.objects.filter(OrganizationId = org).values_list('userId_id', flat=True).distinct()
        print(owner)
        member = TeamMember.objects.filter(Q(OrganizationId = org) & ~Q(userId_id__in = owner)).values_list('userId_id', flat=True).distinct()
        print(member)
        print("org.contactEmail")
        print(org.webSiteLink)
        orgSize = len(owner) + len(member)
        print(f"{os.environ.get('FRONTEND')}/media/{org.logo}")
        return render(request ,"companyProfile.html" , 
            { 
                "slug" : slug ,
                "user" : user,
                "org": org ,
                "page" : "COMPANY_PROFILE" ,
                "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
                "orgSize" : orgSize,
                "endpoint":"organization",
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
        # else:
        #     form.add_error(name ,data.message)
        #     return render(request ,"CreateTeam.html", { 'form' : form })
            
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
            if not isCorrectTime(data["checkInTime"] , data["checkOutTime"]):
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
        org = getOrgBySlug(request , slug)
        print(org)
        team = get_object_or_404(Team , id = teamId)
        print(team)
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

def leaveRequest(request , slug):
    try:
        user = request.session["user"]
        org = Organization.objects.get(slug = slug)
        owner = OwnerDetails.objects.filter(OrganizationId = org).values_list('userId_id', flat=True).distinct()
        print(owner)
        member = TeamMember.objects.filter(Q(OrganizationId = org) & ~Q(userId_id__in = owner)).values_list('userId_id', flat=True).distinct()
        print(member)
        print("org.contactEmail")
        print(org.webSiteLink)
        orgSize = len(owner) + len(member)
        return render(request ,"LeaveRequest.html" , 
                       { 
                "slug" : slug ,
                "user" : user,
                "org": org ,
                "page" : "leave-request" ,
                "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
                "orgSize" : orgSize,
                "endpoint":"organization",
                "baseUrl" : os.environ.get('FRONTEND')
                    } 
                      )
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

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
        search=""
        rows=10
        page=0
        data = request.POST
        print("=============== teams ==================")
        print(data)


        if(data.get("search" , "") not in [None , "" ]):
            search = data["search"]
        
        
        if(data.get("rows" ,"") not in [None , "" ]):
            rows = int(data["rows"])
        
        
        if(data.get("page" , "") not in [None , "" ]):
            page = int(data["page"][0])
        

        print("data ===>")
        print(f"search= {search} rows= {rows} page= {page}")

        org = getOrgBySlug(request , slug)
        skip = page*rows
        orgSize = getOrgSize(org)

        print(f"skip {skip}")

        teamsData = Team.objects.filter(Q(OrganizationId = org) &                                 
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

        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"Team.html" , { 
            "slug" : slug ,
            "org": org ,
            "orgSize":orgSize,
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
        print(tableTitle )
        print(tableData)

        # t.objects.annotate(totalMem = Count("teammember")) 
        return render(request ,"TeamDetails.html" , { 
            "slug" : slug ,
            "org": org ,
            "orgSize":orgSize,
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND'), 
            "endpoint":"organization",
            "page" : "team-details" ,
            "teamName": team.name,
            "teamsMembersDetails" : teamsMembersDetails[ skip :  skip + rows],
            "totalMemeberTeams" : np.arange(0, math.ceil(len(teamsMembersDetails)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "openAction":openAction,
            "editAction":editAction,
            "deleteAction":deleteAction,
            "columnCount":6,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search
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

        org = Organization.objects.get(_id = user["currentActiveOrganization"])

        team = get_object_or_404(Team , id = teamId ,OrganizationId = org )
        print(team)
        print(request.method)

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

        if(request.method == "POST"):
            TeamMember.objects.filter(id = id).delete()
            return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
        else:
            return HttpResponseRedirect(f"/organization/teams/{org.slug}/{teamId}")
    except Exception as e:
        return HttpResponseServerError(e)

def getEmployeeFormatedData(employeeData):
    tableTitle = ["Name","Job Title","Email","DOB","Phone Number","Address","createdAt"]
    tableData = []
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
            f'{emp._id}',
        ])
    return tableTitle , tableData

def employees(request , slug):
    try:
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

        employeeData = Employee.objects.filter(Q(Organization = org) &
         (Q(employee__DOB__icontains=search) |
     Q(employee__phoneNumber__icontains=search) |
     Q(employee__firstName__icontains=search) |
     Q(employee__middleName__icontains=search) |
     Q(employee__lastName__icontains=search) |
     Q(jobTitle__title__icontains=search) |  # Correct field name
     Q(employee__email__icontains=search) |
     Q(employee__address__city__icontains=search) |
     Q(employee__address__state__icontains=search) |
     Q(employee__address__country__icontains=search) |
     Q(employee__address__code__icontains=search))
    ).order_by("-createdAt")
        
        tableTitle , tableData = getEmployeeFormatedData(employeeData)
        openAction = False
        editAction = True
        deleteAction = True
        print(employeeData )
        print(len(employeeData))

        return render(request ,"Employee.html" , { 
            "slug" : slug ,
            "org": org ,
            "orgSize":orgSize,
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

        openAction = True
        editAction = True
        deleteAction = True

        data = { 
            "slug" : slug ,
            "org": org ,
            "orgSize":orgSize,
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

def jobTitleDetails(request , slug ,id):
    try:
        search=""
        rows=10
        page=0
        data = request.POST
        print("======================================================")
        print(id)
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
        jobTitle= get_object_or_404(Job_title , id=id)
        print(jobTitle) 
        print(type(jobTitle)) 
        skip = page*rows
        print(skip) 
        orgSize = getOrgSize(org)
        print(orgSize) 
        print("orgSize") 
        # Name","Job Title","Email","DOB","Phone Number","Address","createdAt"
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
        print("employeeData") 
        print(employeeData) 
        
        tableTitle , tableData = getEmployeeFormatedData(employeeData)
        print(tableTitle)
        print(tableData)

        openAction = False
        editAction = False
        deleteAction = True

        data = { 
            "slug" : slug ,
            "org": org ,
            "orgSize":orgSize,
            "logo" : f"{os.environ.get('FRONTEND')}/media/{org.logo}" ,
            "baseUrl" : os.environ.get('FRONTEND') ,
            "endpoint":"organization",
            "page" : "job-title",
            # "JobTitleData" : tableData
            "totalJobTitle" : np.arange(0, math.ceil(len(employeeData)/10)),
            'tableTitle':tableTitle,
            'tableData':tableData[ skip :  skip + rows],
            "columnCount" : 4,
            "openAction" : openAction,
            "editAction" : editAction,
            "deleteAction" : deleteAction,
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

def AddEmployee(request ):
    try:
        print("entered add employee")
        user = request.session["user"]
        print(user)
        org = Organization.objects.get(_id = user["currentActiveOrganization"])
        print(org)
        if(request.method == "POST"):
            print("post method")
            print(request.POST["email"])
            form = addEmployeeForm( request.POST, organization=org)
            if form.is_valid():
                userToAdd = Users.objects.get(email = request.POST["email"])
                print(userToAdd)
                emp = Employee(
                    employee = userToAdd , 
                    createdBy = Users.objects.get(_id = user["_id"]),
                    Organization = org
                               )
                emp.save()
                return HttpResponseRedirect(f"/organization/{org.slug}")
            else:
                return render(request ,"AddEmployee.html", { 'form' : form })
        else:
            form = addEmployeeForm(organization=org)
            return render(request ,"AddEmployee.html", { 'form' : form })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)

def AddJobTitle(request ):
    try:
        print("entered add job title")
        user = request.session["user"]
        print(user)
        org = Organization.objects.get(_id = user["currentActiveOrganization"])
        print(org)
        if(request.method == "POST"):
            form = addJobTitleForm( request.POST)
            print("post method")
            print(request.POST)
            if form.is_valid():
                newJobTitle = Job_title(
                    title = request.POST["title"] ,
                    Organization = org,
                    createdBy = Users.objects.get(_id = user["_id"])
                    )
                newJobTitle.save()
                return HttpResponseRedirect(f"/organization/{org.slug}")
            else:
                return render(request ,"AddJobTitle.html", { 'form' : form })
        else:
            form = addJobTitleForm()
            return render(request ,"AddJobTitle.html", { 'form' : form })
    except Exception as e:
        print(e)
        return HttpResponseServerError(e)