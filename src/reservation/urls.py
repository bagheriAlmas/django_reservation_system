from django.urls import path

from .views import show_all_listings, show_all_available_listings, add_reservation, overview_reports

urlpatterns = [
    path('listings/', show_all_listings, name='listing-list'),
    path('available_listings/', show_all_available_listings, name='available_listing-list'),
    path('add_reservation/', add_reservation, name='add_reservation'),
    path('reports/', overview_reports, name='overview_reports'),
]