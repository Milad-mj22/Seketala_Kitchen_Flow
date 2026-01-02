from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.shortcuts import render, redirect
from .models import HotelRoom, Guest
from .forms import HotelRoomForm, GuestForm

# Rooms
def room_list(request):
    rooms = HotelRoom.objects.all()
    return render(request, "hotel/room_list.html", {"rooms": rooms})

def add_room(request):
    if request.method == "POST":
        form = HotelRoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("room_list")
    else:
        form = HotelRoomForm()
    return render(request, "hotel/add_room.html", {"form": form})


# Guests
from django.db.models import Sum
from .models import HotelRoom, Guest


from django.db.models import Sum, Count, F
from .models import HotelRoom, Guest

def guest_list(request):
    guests = Guest.objects.select_related("room").filter(show_in_list=True)

    # Overall room summary
    total_rooms = HotelRoom.objects.count()
    total_capacity = HotelRoom.objects.aggregate(total=Sum('room_capacity'))['total'] or 0
    total_persons_inside = Guest.objects.filter(show_in_list=True).aggregate(total=Sum('persons_in_room'))['total'] or 0
    full_rooms = 0
    full_rooms = 0
    for room in HotelRoom.objects.all():
        has_guest = room.guests.filter(show_in_list=True).exists()
        if has_guest:
            full_rooms += 1

    overall_summary = {
        "total_rooms": total_rooms,
        "total_capacity": total_capacity,
        "total_persons_inside": total_persons_inside,
        "full_rooms": full_rooms
    }

    return render(request, "hotel/guest_list.html", {
        "guests": guests,
        "overall_summary": overall_summary
    })


def add_guest(request):
    if request.method == "POST":
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("guest_list")
    else:
        form = GuestForm()
    rooms = HotelRoom.objects.all()
    return render(request, "hotel/add_guest.html", {"form": form,"rooms":rooms})






def edit_guest(request, pk):
    guest = Guest.objects.get(pk=pk)
    if request.method == "POST":
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            return redirect("guest_list")
    else:
        form = GuestForm(instance=guest)

    rooms = HotelRoom.objects.all()
    return render(request, "hotel/add_guest.html", {"form": form, "rooms": rooms, "edit_mode": True})



def delete_guest(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == "POST":
        guest.show_in_list = False
        guest.save()
        return redirect("guest_list")
    # Optional: show confirmation page
    return render(request, "hotel/confirm_delete.html", {"object": guest})