from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login first.")
                return redirect("login")

            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You are not authorized to access this page.")
            if request.user.role == "owner":
                return redirect("owner_dashboard")
            elif request.user.role == "user":
                return redirect("user_dashboard")
            return redirect("login")
        return wrapper_func
    return decorator