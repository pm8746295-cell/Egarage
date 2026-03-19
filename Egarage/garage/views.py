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
    services = ParkingSlot.objects.all()  # <--- NAYI LINE: Database se saari services utha li
    return render(request, "garage/user/user_dashboard.html", {"services": services}) # <--- HTML ko data bhej diya


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

@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def bookService(request, id):
    # 1. Wo specific service database se nikali jise user book karna chahta hai
    service = ParkingSlot.objects.get(id=id)
    
    # 2. Egarage ka service charge (amount)
    amount = 499 
    
    # 3. Jab user 'Pay Now' dabayega (POST request)
    if request.method == "POST":
        service.is_booked = True # Service ko booked mark kar diya
        service.save()           # Database me save kar diya
        return redirect("user_dashboard") # Wapas dashboard par bhej diya
        
    # 4. Normal page load hone par booking.html dikhana
    return render(request, "garage/user/booking.html", {"service": service, "amount": amount})

# --- UPDATE (Edit) SERVICE ---
@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def updateParking(request, id):
    parking = ParkingSlot.objects.get(id=id) # Specific service nikali
    if request.method == "POST":
        # instance=parking likhna zaroori hai taaki purani hi update ho
        form = ParkingSlotCreationForm(request.POST, request.FILES, instance=parking)
        if form.is_valid():
            form.save()
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm(instance=parking) # Purana data form me bhara aayega
    
    return render(request, "garage/owner/update_parking.html", {"form": form})

# --- DELETE SERVICE ---
@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def deleteParking(request, id):
    parking = ParkingSlot.objects.get(id=id)
    parking.delete() # Database se permanently uda diya
    return redirect("owner_dashboard")

