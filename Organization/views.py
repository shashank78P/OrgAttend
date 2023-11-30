from django.shortcuts import render
from Organization.forms import createOrganizationForm, createTeamForm
from Organization.models import Organization ,OwnerDetails
from Users.models import Address, Users

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
    

def createTeam(request):
    print(request.method)
    if(request.method == "POST"):
        form = createTeamForm(request.POST)
        print(request.POST)
        return render(request ,"CreateTeam.html", { 'form' : form })
    else:
        form = createTeamForm()
        return render(request ,"CreateTeam.html", { 'form' : form })