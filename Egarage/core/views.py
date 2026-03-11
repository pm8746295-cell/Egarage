from django.shortcuts import render,redirect,HttpResponse
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def userSignupView(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        #email send
        email = form.cleaned_data['email']
        send_mail(subject="welcome to find my garage",message="Thank you for registering with Find My Garage.",from_email=settings.EMAIL_HOST_USER,recipient_list=[email])
        form.save()
        return redirect('login') #error
      else:
        return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request,'core/signup.html',{'form':form})


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