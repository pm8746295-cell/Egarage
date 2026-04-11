from django.shortcuts import render,redirect,HttpResponse
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

# Create your views here.
def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST or None)
        if form.is_valid():
            user = form.save()

            try:
                user_name = f"{user.first_name} {user.last_name}".strip()
                if not user_name:
                    user_name = user.email

                user_role = user.role if hasattr(user, 'role') else "Customer"
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
                login_link = f"{protocol}://{domain}/core/login/"

                subject = "Welcome to Egarage – Your Account is Ready! 🚗✨"
                message = f"""Hello {user_name},

🎉 Welcome to Egarage!

Your account has been successfully created and you are now part of our community.

🔹 Role: {user_role.capitalize()}
🔹 Status: Active

👉 Login to your dashboard and start using our services:
{login_link}

If you have any questions, feel free to reply to this email.

Thank you,
Team Egarage
"""

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True
                )

            except Exception as e:
                print("Email nahi gaya, Error:", e)

            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})


def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)
                if user.role == "owner":
                    return redirect("owner_dashboard")
                elif user.role == "user":
                    return redirect("user_dashboard")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please enter valid login details.")
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})
  
def userLogoutView(request):
    logout(request) # Ye user ko system se bahar nikal dega
    return redirect('login') # Logout hone ke baad wapas login page par bhej dega  

def homeView(request):
    # Agar user pehle se login hai, toh usko direct uske dashboard par bhej do
    if request.user.is_authenticated:
        if getattr(request.user, 'role', '') == 'owner':
            return redirect('owner_dashboard')
        else:
            return redirect('user_dashboard')
            
    # Agar login nahi hai, toh Premium Landing Page dikhao
    return render(request, 'core/home.html')