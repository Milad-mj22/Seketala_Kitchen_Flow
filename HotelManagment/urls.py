from django.urls import path
from . import views

urlpatterns = [
    # Rooms
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/add/", views.add_room, name="add_room"),

    # Guests
    path("guests/", views.guest_list, name="guest_list"),
    path("guests/add/", views.add_guest, name="add_guest"),

    path('guests/edit/<int:pk>/', views.edit_guest, name='edit_guest'),
    path('guests/delete/<int:pk>/', views.delete_guest, name='delete_guest')

]
