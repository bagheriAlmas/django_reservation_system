from django.contrib import admin
from .models import Listing,Reservation

admin.site.register(Listing)
admin.site.register(Reservation)