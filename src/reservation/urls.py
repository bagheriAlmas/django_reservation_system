from django.urls import path

from reservation.views.function_views import (show_all_listings, show_all_available_listings, add_reservation,
                                              overview_reports, listing_details)
from .views.class_views import (ShowAllListingsView, ShowAllAvailableListingsView, AddReservationView, OverviewReportsView,
                                ListingDetailsView)

urlpatterns = [
    # Function Views
    path('v1/listings/', show_all_listings, name='listing-list'),
    path('v1/available_listings/', show_all_available_listings, name='available-listing-list'),
    path('v1/add_reservation/', add_reservation, name='add-reservation'),
    path('v1/reports/', overview_reports, name='overview-reports'),
    path('v1/reports/<int:pk>/', listing_details, name='listing-details'),
    # Class-Base Views
    path('v2/listings/', ShowAllListingsView.as_view(), name='class-listing-list'),
    path('v2/available_listings/', ShowAllAvailableListingsView.as_view(), name='class-available-listing-list'),
    path('v2/add_reservation/', AddReservationView.as_view(), name='class-add-reservation'),
    path('v2/reports/', OverviewReportsView.as_view(), name='class-overview-reports'),
    path('v2/reports/', ListingDetailsView.as_view(), name='class-listing-details'),
]
