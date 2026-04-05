from django.shortcuts import render,redirect,HttpResponse
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST or None)
        if form.is_valid():
            # STEP 1: Save User
            user = form.save()
            
            # STEP 2: Professional Dynamic Email Logic
            try:
                user_name = user.first_name if user.first_name else user.email
                user_role = user.role if hasattr(user, 'role') else "Customer"
                
                # Yeh line MAGIC karegi! (Dynamic Domain)
                # Agar localhost pe ho toh '127.0.0.1:8000' nikalega, aur live pe ho toh 'www.egarage.com'
                domain = request.get_host() 
                protocol = 'https' if request.is_secure() else 'http'
                login_link = f"{protocol}://{domain}/core/login/"

                subject = "Welcome to Egarage – Your Account is Ready! 🚗✨"
                
                # Naya "Pro Email" Format (Jaisa aapne suggest kiya)
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
(Managed by Mihir Patel)
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

            # STEP 3: Redirect
            return redirect('login')
            
        else:
            return render(request, 'core/signup.html', {'form': form})  
    else:
        form = UserSignupForm()
        return render(request, 'core/signup.html', {'form': form})


def userLoginView(request):
  if request.method =="POST":
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
      print(form.cleaned_data)
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      user = authenticate(request,email=email,password=password) #it will check in database..
      if user:
        login(request,user)
        if user.role == "owner":
          return redirect("owner_dashboard") #garage.urls.py name...
        elif user.role == "user":
          return redirect("user_dashboard") #garage.urls.py name...
      else:
        return render(request,'core/login.html',{'form':form})  
    
  else:
    form = UserLoginForm()
    return render(request,'core/login.html',{'form':form})
  
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