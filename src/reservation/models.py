from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Reservation(models.Model):
    listing = models.ForeignKey(Listing, related_name='reservations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.listing.id} - {self.listing.name} - {self.name}"

    def clean(self):
        # Ensure end_time is greater than start_time
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End time must be greater than start time")

    def get_difference_date_days(self):
        difference = self.end_date - self.start_date
        return difference.days + 1