from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ParkingSlotCreationForm
from .models import ParkingSlot
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import datetime

User = get_user_model()


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def ownerDashboardView(request):
    query = request.GET.get('q')

    parkings = ParkingSlot.objects.filter(owner=request.user).order_by('-created_at')

    if query:
        parkings = parkings.filter(name__icontains=query)

    total_services = ParkingSlot.objects.filter(owner=request.user).count()
    active_bookings = ParkingSlot.objects.filter(
        owner=request.user,
        is_booked=True,
        status__in=['pending', 'approved']
    ).count()
    completed_bookings = ParkingSlot.objects.filter(
        owner=request.user,
        status='completed'
    ).count()

    total_earnings = ParkingSlot.objects.filter(
        owner=request.user,
        status='completed'
    ).exclude(amount__isnull=True)

    total_earnings_value = sum(service.amount for service in total_earnings)

    context = {
        "parkings": parkings,
        "total_services": total_services,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "total_earnings": total_earnings_value,
    }

    return render(request, "garage/owner/owner_dashboard.html", context)


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def userDashboardView(request):
    query = request.GET.get('q')

    services = ParkingSlot.objects.all().order_by('-created_at')
    if query:
        services = services.filter(name__icontains=query)

    my_history = ParkingSlot.objects.filter(booked_by=request.user).order_by('-updated_at')

    return render(
        request,
        "garage/user/user_dashboard.html",
        {
            "services": services,
            "my_history": my_history
        }
    )


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def createParking(request):
    if request.method == "POST":
        form = ParkingSlotCreationForm(request.POST, request.FILES)
        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.owner = request.user

            # Naya service create karte waqt default state clean rakho
            if not new_service.is_booked:
                new_service.booked_by = None
                new_service.status = 'pending'

            new_service.save()
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm()

    return render(request, "garage/owner/create_parking.html", {"form": form})


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def bookService(request, id):
    service = get_object_or_404(ParkingSlot, id=id)

    if service.is_booked:
        return redirect("user_dashboard")

    amount = service.amount if service.amount else 499

    if request.method == "POST":
        service.is_booked = True
        service.booked_by = request.user
        service.status = 'pending'
        service.save()

        try:
            subject = f"Egarage - Booking Confirmed: {service.name}"
            message = (
                f"Hello {request.user.first_name or request.user.email},\n\n"
                f"Your booking for '{service.name}' has been confirmed successfully.\n"
                f"Amount to be paid at garage: ₹{amount}.\n\n"
                f"Thank you for choosing Egarage!\n"
                f"- Team Egarage"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=True
            )
        except Exception as e:
            print("Email nahi gaya, Error:", e)

        return redirect("user_dashboard")

    return render(
        request,
        "garage/user/booking.html",
        {
            "service": service,
            "amount": amount
        }
    )


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def updateParking(request, id):
    parking = get_object_or_404(ParkingSlot, id=id, owner=request.user)

    if request.method == "POST":
        form = ParkingSlotCreationForm(request.POST, request.FILES, instance=parking)
        if form.is_valid():
            updated_service = form.save(commit=False)

            # Agar owner manually unavailable hata de to booking info reset ho
            if not updated_service.is_booked:
                updated_service.booked_by = None
                if updated_service.status == 'approved':
                    updated_service.status = 'pending'

            updated_service.save()
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm(instance=parking)

    return render(request, "garage/owner/update_parking.html", {"form": form})


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def deleteParking(request, id):
    parking = get_object_or_404(ParkingSlot, id=id, owner=request.user)
    parking.delete()
    return redirect("owner_dashboard")


@login_required(login_url="login")
def editProfile(request):
    if request.method == "POST":
        current_user = User.objects.get(id=request.user.id)
        current_user.first_name = request.POST.get('first_name')
        current_user.last_name = request.POST.get('last_name')
        current_user.mobile = request.POST.get('mobile')
        current_user.save()

        if current_user.role == 'owner':
            return redirect("owner_dashboard")
        return redirect("user_dashboard")

    return render(request, "garage/edit_profile.html", {"user": request.user})


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def cancelBooking(request, id):
    service = get_object_or_404(ParkingSlot, id=id, booked_by=request.user)

    service.is_booked = False
    service.booked_by = None
    service.status = 'cancelled'
    service.save()

    return redirect("user_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def generateInvoice(request, id):
    service = get_object_or_404(ParkingSlot, id=id, booked_by=request.user)

    today = datetime.date.today()
    invoice_date = today.strftime("%d %B %Y")
    invoice_no = f"INV-{today.year}-{service.id:04d}"
    amount = service.amount if service.amount else 499

    context = {
        "service": service,
        "user": request.user,
        "invoice_date": invoice_date,
        "invoice_no": invoice_no,
        "amount": amount,
    }

    return render(request, "garage/user/invoice.html", context)


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def approveBooking(request, id):
    booking = get_object_or_404(ParkingSlot, id=id, owner=request.user)
    booking.status = 'approved'
    booking.save()
    return redirect("owner_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def rejectBooking(request, id):
    booking = get_object_or_404(ParkingSlot, id=id, owner=request.user)
    booking.status = 'cancelled'
    booking.is_booked = False
    booking.booked_by = None
    booking.save()
    return redirect("owner_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def completeBooking(request, id):
    booking = get_object_or_404(ParkingSlot, id=id, owner=request.user)
    booking.status = 'completed'
    booking.is_booked = False
    booking.booked_by = None
    booking.save()
    return redirect("owner_dashboard")