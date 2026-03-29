from django.urls import path
from . import views

urlpatterns = [
    path("owner/",views.ownerDashboardView,name="owner_dashboard"),
    path("user/",views.userDashboardView,name="user_dashboard"),
    path("createparking/",views.createParking,name="create_parking"),
    path('user/book-service/<int:id>/', views.bookService, name='book_service'),
    path('owner/update-service/<int:id>/', views.updateParking, name='update_parking'),
    path('owner/delete-service/<int:id>/', views.deleteParking, name='delete_parking'),
    path('edit-profile/', views.editProfile, name='edit_profile'),
    path('user/cancel-booking/<int:id>/', views.cancelBooking, name='cancel_booking'),
    path('user/invoice/<int:id>/', views.generateInvoice, name='generate_invoice'),
    path('approve/<int:id>/', views.approveBooking, name='approve_booking'),
    path('reject/<int:id>/', views.rejectBooking, name='reject_booking'),
    path('complete/<int:id>/', views.completeBooking, name='complete_booking')
]