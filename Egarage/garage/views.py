from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ParkingSlotCreationForm
from .models import ParkingSlot  # <--- NAYI LINE: Database table import kiya

# Create your views here.
#@login_required(login_url="login") #check in core.urls.py login name should exist..
@role_required(allowed_roles=["owner"]) #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    parkings = ParkingSlot.objects.all()  # <--- NAYI LINE: Database se saari parking details uthayi
    return render(request, "garage/owner/owner_dashboard.html", {"parkings": parkings}) # <--- NAYI LINE: HTML ko data bheja

#@login_required(login_url="login")
@role_required(allowed_roles=["user"]) #check in core.urls.py login name should exist.. 
def userDashboardView(request):
    return render(request,"garage/user/user_dashboard.html")


def createParking(request):
    if request.method =="POST":
        print(request.POST)
        form = ParkingSlotCreationForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect("owner_dashboard")
            #return render(request,"htm",{parkings:parking})
    else:
        form = ParkingSlotCreationForm()
    return render(request,"garage/owner/create_parking.html",{"form":form})