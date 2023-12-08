import math
import os
from django.http import HttpResponseServerError , HttpResponseNotAllowed, JsonResponse , Http404 , HttpResponseRedirect
from django.shortcuts import render , get_object_or_404
import requests
from Organization.forms import createOrganizationForm, createTeamForm , addEmployeeForm , addJobTitleForm
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

def saveTeamMemberData(request,user , form , role , team , name , orgId):
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
            createdBy = Users.objects.filter(email = user._id)
            teamMem = TeamMember(
                userId = user,
                role = role,
                TeamId = team,
                OrganizationId = orgId,
                createdBy = createdBy[0]
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

def createTeam(request):
    try:
        print(request.method)
        user = request.session["user"]
        if(request.method == "POST"):
            isUserPermittedToAdd(request)
            print(request.POST)
            form = createTeamForm(request.POST)
            data = request.POST
            print(data)
            print(type(data))
            createdBy = Users.objects.get(_id = user["_id"])
            org_id = Organization.objects.get(_id = user["currentActiveOrganization"])
            team = Team(
                   name = data["name"],
                   OrganizationId = org_id,
                   checkInTime = datetime.strptime(data["checkInTime"], "%I:%M %p").time(),
                   checkOutTime = datetime.strptime(data["checkOutTime"], "%I:%M %p").time(),
                   description = data["description"],
                   createdBy = createdBy
            )

            team.save()
        
            # leader
            print("team leader")
            print(data["leader"])
            leaderData = Users.objects.filter(email = data["leader"])
            print(leaderData)
            if len(leaderData) == 1:
                saveTeamMemberData(request,leaderData[0] , form , "LEADER" ,team , "leader" , org_id)
            
            # co_Leader
            co_leader = data["co_Leader"].split(",")
            for email in co_leader:
                co_Leader_Data = Users.objects.filter(email = email)
                if len(co_Leader_Data) == 1:
                    saveTeamMemberData(request,co_Leader_Data[0] , form , "CO-LEADER",team , "co_Leader", org_id)
            
            # team_members
            team_members = data["team_members"].split(",")
            for email in team_members:
                member_Data = Users.objects.filter(email = email)
                if len(member_Data) ==1:
                    saveTeamMemberData(request,member_Data[0] , form , "MEMBER" , team , "team_members",org_id)
                
            print(org_id.slug)
            return HttpResponseRedirect(f"/organization/{org_id.slug}")
            
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })
    except():
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })

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

def getTeamsMemebesFormatedData(TeamsMembersData):
    tableTitle = ["name","role","createdBy","createdAt"]
    tableData = []
    print(tableTitle)
    for i in  range(0,len(TeamsMembersData)):
        teamMember = TeamsMembersData[i]
        print(teamMembersDetails)
    
        tableData.append([ 
            f'{teamMember.userId.firstName} {teamMember.userId.middleName} {teamMember.userId.lastName}',
            f'{teamMember.role}',
            f'{teamMember.createdBy.firstName} {teamMember.createdBy.middleName} {teamMember.createdBy.lastName}',
            f'{teamMember.createdAt}',
            f'{teamMember.id}',
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
        
        tableTitle , tableData = getTeamsMemebesFormatedData(teamsMembersDetails)
        openAction = False
        editAction = False
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
            "columnCount":5,
            "pageNo":page,
            "skip":skip,
            "rows":rows,
            "search":search
             })
    except Exception as e:
        print(e)
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