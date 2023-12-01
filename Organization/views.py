from django.http import HttpResponseServerError , HttpResponseNotAllowed, JsonResponse , Http404
from django.shortcuts import render
import requests
from Organization.forms import createOrganizationForm, createTeamForm
from Organization.models import Organization ,OwnerDetails , Team ,TeamMember
from Users.models import Address, Users
from Users.views import getUserByEmail

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
        return render(request ,"companyProfile.html" , { "slug" : slug})
    except():
        return render(request ,"companyProfile.html")        

def companyRole(request , slug):
    try:
        return render(request ,"createEmployeeRole.html")
    except():
        return render(request ,"createEmployeeRole.html")

def saveTeamMemberData(request,data , form , role , team , name):
    try:
        if not data.error:
            teamMem = TeamMember(
                userId = data,
                role = role,
                TeamId = team
            )
            teamMem.save()
        else:
            form.add_error(name ,data.message)
            return render(request ,"CreateTeam.html", { 'form' : form })
            
    except Exception as e:
        return
    
def getAllOrganizationList(request) :
    try:
        print("getAllOrganizationList")
        user = request.session["user"]
        print(user)

        # getting all companies of a user
        data = TeamMember.objects.filter( userId =3 ).values_list('OrganizationId', flat=True).distinct()

        all_org = []
        org_data = Organization.objects.filter(_id__in = data)

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
        user = request.session['user']
        print(user)

        
    except:
        return HttpResponseNotAllowed("U don't have a permission")

def createTeam(request):
    try:
        print(request.method)
        if(request.method == "POST"):
            print(request.POST)
            form = createTeamForm(request.POST)
            data = request.POST
            team = Team(
                   name = data.name,
                   OrganizationId = 2,
                   checkInTime = data.checkInTime,
                   checkOutTime = data.checkOutTime,
                   description = data.description,
            )

            team.save()
        
            # leader
            leaderData = getUserByEmail(data.leader)
            saveTeamMemberData(request,leaderData , form , "LEADER" ,team , "leader")
            
            # co_Leader
            co_leader = data.co_Leader.split(",")
            for email in co_leader:
                co_Leader_Data = getUserByEmail(email)
                saveTeamMemberData(request,co_Leader_Data , form , "CO-LEADER",team , "co_Leader")
            
            # team_members
            team_members = getUserByEmail(data.team_members).split(",")
            for email in team_members:
                member_Data = getUserByEmail(email)
                saveTeamMemberData(request,member_Data , form , "MEMBER" , team , "team_members")
                
            return render(request ,"companyProfile.html")
            
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })
    except():
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })

