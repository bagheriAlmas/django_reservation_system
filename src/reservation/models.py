from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class ListingOwner(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    listing = models.ForeignKey(ListingOwner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.listing.id} - {self.listing.name} - {self.name}"

    def clean(self):
        # Ensure end_time is greater than start_time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be greater than start time")