from django.urls import path
from . import views

urlpatterns = [
    path("owner/",views.ownerDashboardView,name="owner_dashboard"),
    path("user/",views.userDashboardView,name="user_dashboard"),
    path("createparking/",views.createParking,name="create_parking"),
    path('user/book-service/<int:id>/', views.bookService, name='book_service'),
    path('owner/update-service/<int:id>/', views.updateParking, name='update_parking'),
    path('owner/delete-service/<int:id>/', views.deleteParking, name='delete_parking')
]