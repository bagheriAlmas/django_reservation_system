from django.db.models import Q
from datetime import datetime

from rest_framework.exceptions import ValidationError

from .models import Listing


def available_listings_in_date_range_query(start_date, end_date):
    unavailable_listings = Listing.objects.filter(
        Q(reservations__start_date__lte=start_date, reservations__end_date__gte=start_date) |
        Q(reservations__start_date__lte=end_date, reservations__end_date__gte=end_date) |
        Q(reservations__start_date__gte=start_date, reservations__end_date__lte=end_date)
    )

    available_listings = Listing.objects.exclude(id__in=unavailable_listings.values_list('id', flat=True))
    return available_listings



def parse_input_dates(start_date, end_date):
    if start_date is None or end_date is None:
        raise ValidationError('Both start_date and end_date are required.')

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if start_date < datetime.today().date() or end_date < datetime.today().date():
        raise ValidationError('The selected day must not be a past date.')

    if start_date > end_date:
        raise ValidationError('Start date must be before end date.')
    return start_date, end_date


