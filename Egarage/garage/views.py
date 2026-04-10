from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ParkingSlotCreationForm
from .models import ParkingSlot  # <--- NAYI LINE: Database table import kiya
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.mail import send_mail
from django.conf import settings
import datetime



# Create your views here.
@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def ownerDashboardView(request):
    query = request.GET.get('q')
    if query:
        parkings = ParkingSlot.objects.filter(name__icontains=query)
    else:
        parkings = ParkingSlot.objects.all()

    # --- NAYA PRO LOGIC FOR ANALYTICS ---
    total_services = ParkingSlot.objects.count()
    
    # 1. Jo gaadiyan abhi garage mein hain (Pending/Approved)
    active_bookings = ParkingSlot.objects.filter(is_booked=True).count()
    
    # 2. Jo gaadiyan service ho chuki hain (Completed)
    completed_bookings = ParkingSlot.objects.filter(status='Completed').count()
    
    # 3. Total Earnings = (Active gaadiyan + Complete ho chuki gaadiyan) * 499
    # Ab paise kabhi kam nahi honge!
    total_earnings = (active_bookings + completed_bookings) * 499

    context = {
        "parkings": parkings,
        "total_services": total_services,
        "active_bookings": active_bookings,
        "total_earnings": total_earnings
    }
    
    return render(request, "garage/owner/owner_dashboard.html", context)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

@login_required(login_url="login")
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
        form = ParkingSlotCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Form ko hold par rakho (direct save mat karo)
            new_service = form.save(commit=False)
            
            # 2. Jo user login hai, usko is service ka owner bana do
            new_service.owner = request.user
            
            # 3. Ab data ekdum complete hai, isko database me save kar do
            new_service.save()
            
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm()
        
    return render(request, "garage/owner/create_parking.html", {"form":form})

@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def bookService(request, id):
    service = ParkingSlot.objects.get(id=id)
    amount = 499 
    
    if request.method == "POST":
        service.is_booked = True 
        service.booked_by = request.user
        service.status = 'pending'  
        service.save()           
        
        
        try:
            subject = f"Egarage - Booking Confirmed: {service.name}"
            # Message mein humne aapka naam bhi daal diya as developer! 😎
            message = f"Hello {request.user.first_name},\n\nYour booking for '{service.name}' has been confirmed successfully.\nAmount to be paid at garage: ₹499.\n\nThank you for choosing Egarage!\n- Developed by Mihir Patel"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email], fail_silently=True)
        except Exception as e:
            print("Email nahi gaya, Error:", e)
        

        return redirect("user_dashboard") 
        
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

@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def cancelBooking(request, id):
    service = ParkingSlot.objects.get(id=id)

    if service.booked_by == request.user:
        service.is_booked = False
        service.booked_by = None
        service.status = 'pending'
        service.save()

    return redirect("user_dashboard")

@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def generateInvoice(request, id):
    # Jis service ka bill chahiye, use uthao
    service = ParkingSlot.objects.get(id=id)

    # Ek basic security check (Sirf wahi user apna bill dekh paye jisne book kiya hai)
    if service.booked_by != request.user:
        return redirect("user_dashboard")

    # --- NAYA LOGIC: SMART INVOICE GENERATOR ---
    
    # 1. Aaj ki date nikalenge (Format: 04 April 2026)
    today = datetime.date.today()
    invoice_date = today.strftime("%d %B %Y") 
    
    # 2. Ek unique Invoice Number banayenge (Year + Service ID combination)
    # Zfill (04d) lagane se ID=8 ban jayega '0008' jisse real bill feel aayega
    invoice_no = f"INV-{today.year}-{service.id:04d}"

    # 3. Context mein naye variables pass karenge
    context = {
        "service": service, 
        "user": request.user,
        "invoice_date": invoice_date,
        "invoice_no": invoice_no
    }

    return render(request, "garage/user/invoice.html", context)


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def approveBooking(request, id):
    booking = ParkingSlot.objects.get(id=id)
    booking.status = 'approved'
    booking.save()
    return redirect("owner_dashboard")

@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def rejectBooking(request, id):
    booking = ParkingSlot.objects.get(id=id)
    booking.status = 'pending'
    booking.is_booked = False
    booking.booked_by = None
    booking.save()
    return redirect("owner_dashboard")

@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def completeBooking(request, id):
    booking = ParkingSlot.objects.get(id=id)
    booking.status = 'completed'
    booking.is_booked = False
    booking.save()
    return redirect("owner_dashboard")


