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
            # STEP 1: Pehle user ko save karo taaki uski details mil sakein
            user = form.save()
            
            # STEP 2: Professional Email Bhejne ka Logic
            try:
                # User ka naam nikalo (agar naam nahi diya toh email use karo)
                user_name = user.first_name if user.first_name else user.email
                user_role = user.role if hasattr(user, 'role') else "Customer"
                
                # Professional Subject
                subject = "Welcome to Egarage – Your Account is Ready! 🚗✨"
                
                # Professional Message Body (f-string ka use karke)
                message = f"""Hi {user_name},

Welcome to Egarage! We are excited to have you on board.

Your account has been created successfully. Here are your account details:

- Role: {user_role.capitalize()}
- Account Status: Active

You can now log in to your dashboard to explore our services, book appointments, or manage your garage listings.

Login Here: http://127.0.0.1:8000/core/login/

If you have any questions or need assistance, feel free to reply to this email.

Best Regards,
Team Egarage
(Managed by Mihir Patel)
"""
                # Mail bhejne ki final command
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception as e:
                print("Email nahi gaya, Error:", e)

            # STEP 3: Mail bhejne ke baad user ko login page par bhej do
            return redirect('login')
            
        else:
            # Agar form mein koi error ho
            return render(request, 'core/signup.html', {'form': form})  
    else:
        # Jab user pehli baar signup page khole
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