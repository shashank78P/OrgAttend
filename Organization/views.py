from django.http import HttpResponseServerError , HttpResponseNotAllowed, JsonResponse , Http404 , HttpResponseRedirect
from django.shortcuts import render
import requests
from Organization.forms import createOrganizationForm, createTeamForm
from Organization.models import Organization ,OwnerDetails , Team ,TeamMember
from Users.models import Address, Users
from Users.views import getUserByEmail
from django.db.models import Q
from datetime import datetime

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
        return render(request ,"companyProfile.html" , { "slug" : slug , "user" : user, "org": org , "page" : "COMPANY_PROFILE"})
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
            teamMem = TeamMember(
                userId = user,
                role = role,
                TeamId = team,
                OrganizationId = orgId
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

            # team.save()
        
            # leader
            print("team leader")
            print(data["leader"])
            leaderData = getUserByEmail(data["leader"])
            print(leaderData)
            # saveTeamMemberData(request,leaderData , form , "LEADER" ,team , "leader" , org_id)
            
            # co_Leader
            co_leader = data["co_Leader"].split(",")
            for email in co_leader:
                co_Leader_Data = getUserByEmail(email)
                # saveTeamMemberData(request,co_Leader_Data , form , "CO-LEADER",team , "co_Leader", org_id)
            
            # team_members
            team_members = data["team_members"].split(",")
            for email in team_members:
                member_Data = getUserByEmail(email)
                # saveTeamMemberData(request,member_Data , form , "MEMBER" , team , "team_members",org_id)
                
            print(org_id.slug)
            return HttpResponseRedirect(f"/organization/{org_id.slug}")
            
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })
    except():
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })

