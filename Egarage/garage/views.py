from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ParkingSlotCreationForm
from .models import ParkingSlot  # <--- NAYI LINE: Database table import kiya
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
#@login_required(login_url="login") #check in core.urls.py login name should exist..
@role_required(allowed_roles=["owner"]) #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    query = request.GET.get('q') # URL se search word uthaya
    if query:
        # Agar kuch search kiya hai, toh sirf matching naam wale dikhao (icontains = case insensitive search)
        parkings = ParkingSlot.objects.filter(name__icontains=query)
    else:
        # Warna saari services dikhao
    
         parkings = ParkingSlot.objects.all()  # <--- NAYI LINE: Database se saari parking details uthayi
    return render(request, "garage/owner/owner_dashboard.html", {"parkings": parkings}) # <--- NAYI LINE: HTML ko data bheja

#@login_required(login_url="login")
@role_required(allowed_roles=["user"]) #check in core.urls.py login name should exist.. 
def userDashboardView(request):
    query = request.GET.get('q') # User dashboard ke liye bhi same search
    if query:
        services = ParkingSlot.objects.filter(name__icontains=query)
    else:

        services = ParkingSlot.objects.all()  # <--- NAYI LINE: Database se saari services utha li
    my_history = ParkingSlot.objects.filter(booked_by=request.user)
    return render(request, "garage/user/user_dashboard.html", {"services": services, "my_history": my_history})

   

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
        service.booked_by = request.user
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


@login_required(login_url="login")
def editProfile(request):
    if request.method == "POST":
        # 1. Asali user ko database se nikalo
        current_user = User.objects.get(id=request.user.id)
        
        # 2. Form ka data usme daalo
        current_user.first_name = request.POST.get('first_name')
        current_user.last_name = request.POST.get('last_name')
        current_user.mobile = request.POST.get('mobile')
        
        # 3. Database me permanently save karo
        current_user.save() 
        
        if current_user.role == 'owner':
            return redirect("owner_dashboard")
        else:
            return redirect("user_dashboard")
            
    return render(request, "garage/edit_profile.html", {"user": request.user})

