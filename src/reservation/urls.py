from django.urls import path

from .views import show_all_listings

urlpatterns = [
    path('listings/', show_all_listings, name='listing-list'),
]