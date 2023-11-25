from django.urls import path

from reservation.views.function_views import show_all_listings, show_all_available_listings, add_reservation, overview_reports
from .views.class_views import ShowAllListings, ShowAllAvailableListings, AddReservationView, OverviewReportsView
urlpatterns = [
    # Function Views
    path('v1/listings/', show_all_listings, name='listing-list'),
    path('v1/available_listings/', show_all_available_listings, name='available_listing-list'),
    path('v1/add_reservation/', add_reservation, name='add_reservation'),
    path('v1/reports/', overview_reports, name='overview_reports'),
    #Class-Base Views
    path('v2/listings/', ShowAllListings.as_view(), name='class_listing-list'),
    path('v2/available_listings/', ShowAllAvailableListings.as_view(), name='class_available_listing-list'),
    path('v2/add_reservation/', AddReservationView.as_view(), name='class_add_reservation'),
    path('v2/reports/', OverviewReportsView.as_view(), name='class_overview_reports'),
]