from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ParkingSlotCreationForm
from .models import ParkingSlot, Booking
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import datetime
from django.contrib import messages

User = get_user_model()


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def ownerDashboardView(request):
    query = request.GET.get('q')

    parkings = ParkingSlot.objects.filter(owner=request.user).order_by('-created_at')
    if query:
        parkings = parkings.filter(name__icontains=query)

    total_services = ParkingSlot.objects.filter(owner=request.user).count()
    active_bookings = Booking.objects.filter(
        owner=request.user,
        status__in=['pending', 'approved']
    ).count()

    completed_bookings = Booking.objects.filter(
        owner=request.user,
        status='completed'
    )

    total_earnings_value = sum(booking.amount for booking in completed_bookings)

    context = {
        "parkings": parkings,
        "total_services": total_services,
        "active_bookings": active_bookings,
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

    my_history = Booking.objects.filter(user=request.user).order_by('-booking_date')

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
            new_service.is_booked = False
            new_service.booked_by = None
            new_service.status = 'available'
            new_service.save()

            messages.success(request, "Service added successfully.")
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm()

    return render(request, "garage/owner/create_parking.html", {"form": form})


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def bookService(request, id):
    service = get_object_or_404(ParkingSlot, id=id)

    if service.is_booked:
        messages.error(request, "This service is currently unavailable.")
        return redirect("user_dashboard")

    already_exists = Booking.objects.filter(
        service=service,
        user=request.user,
        status__in=['pending', 'approved']
    ).exists()

    if already_exists:
        messages.warning(request, "You already have an active booking for this service.")
        return redirect("user_dashboard")

    amount = service.amount if service.amount else 499

    if request.method == "POST":
        Booking.objects.create(
            service=service,
            user=request.user,
            owner=service.owner,
            amount=amount,
            status='pending'
        )

        service.is_booked = True
        service.booked_by = request.user
        service.status = 'pending'
        service.save()

        try:
            subject = f"Egarage - Booking Confirmed: {service.name}"
            message = (
                f"Hello {request.user.first_name or request.user.email},\n\n"
                f"Your booking request for '{service.name}' has been submitted successfully.\n"
                f"Amount: ₹{amount}\n"
                f"Current Status: Pending\n\n"
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

        messages.success(request, "Booking request submitted successfully.")
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
                updated_service.status = 'available'
                if updated_service.status == 'approved':
                    updated_service.status = 'pending'

            updated_service.save()
            messages.success(request, "Service updated successfully.")
            return redirect("owner_dashboard")
    else:
        form = ParkingSlotCreationForm(instance=parking)

    return render(request, "garage/owner/update_parking.html", {"form": form})


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def deleteParking(request, id):
    parking = get_object_or_404(ParkingSlot, id=id, owner=request.user)
    parking.delete()
    messages.success(request, "Service deleted successfully.")
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
    booking = get_object_or_404(Booking, id=id, user=request.user)

    if booking.status not in ['pending', 'approved']:
        messages.warning(request, "This booking cannot be cancelled now.")
        return redirect("user_dashboard")

    booking.status = 'cancelled'
    booking.save()

    service = booking.service
    service.is_booked = False
    service.booked_by = None
    service.status = 'available'
    service.save()

    messages.success(request, "Booking cancelled successfully.")
    return redirect("user_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["user"])
def generateInvoice(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)

    today = datetime.date.today()
    invoice_date = today.strftime("%d %B %Y")
    invoice_no = f"INV-{today.year}-{booking.id:04d}"

    context = {
        "booking": booking,
        "service": booking.service,
        "user": request.user,
        "invoice_date": invoice_date,
        "invoice_no": invoice_no,
        "amount": booking.amount,
    }

    return render(request, "garage/user/invoice.html", context)

@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def approveBooking(request, id):
    booking = get_object_or_404(Booking, id=id, owner=request.user)

    if booking.status != 'pending':
        messages.warning(request, "Only pending bookings can be approved.")
        return redirect("owner_dashboard")

    booking.status = 'approved'
    booking.save()

    service = booking.service
    service.status = 'approved'
    service.is_booked = True
    service.booked_by = booking.user
    service.save()

    messages.success(request, "Booking approved successfully.")
    return redirect("owner_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def rejectBooking(request, id):
    booking = get_object_or_404(Booking, id=id, owner=request.user)

    if booking.status != 'pending':
        messages.warning(request, "Only pending bookings can be rejected.")
        return redirect("owner_dashboard")

    booking.status = 'rejected'
    booking.save()

    service = booking.service
    service.status = 'available'
    service.is_booked = False
    service.booked_by = None
    service.save()

    messages.success(request, "Booking rejected successfully.")
    return redirect("owner_dashboard")


@login_required(login_url="login")
@role_required(allowed_roles=["owner"])
def completeBooking(request, id):
    booking = get_object_or_404(Booking, id=id, owner=request.user)

    if booking.status != 'approved':
        messages.warning(request, "Only approved bookings can be marked completed.")
        return redirect("owner_dashboard")

    booking.status = 'completed'
    booking.save()

    service = booking.service
    service.status = 'available'
    service.is_booked = False
    service.booked_by = None
    service.save()

    messages.success(request, "Service marked as completed.")
    return redirect("owner_dashboard")