from django.contrib import admin
from .models import Listing, Reservation


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 1


class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'description')
    search_fields = ('name', 'owner__username', 'address')
    list_filter = ('name', 'address')
    inlines = [ReservationInline, ]


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'listing', 'start_date', 'end_date', 'duration')
    search_fields = ('name', 'listing__name', 'listing__owner__username')
    list_filter = ('start_date', 'end_date')
    date_hierarchy = 'start_date'


admin.site.register(Listing, ListingAdmin)
admin.site.register(Reservation, ReservationAdmin)
