from django.urls import path

from .views import show_all_listings, show_all_available_listing

urlpatterns = [
    path('listings/', show_all_listings, name='listing-list'),
    path('available_listings/', show_all_available_listing, name='available_listing-list'),
]