from datetime import datetime
from django.db.models import Q
from .models import Listing


def is_valid_date_format(date_string):
    print(date_string)
    print(type(date_string))
    try:
        datetime.strptime(str(date_string), '%Y-%m-%d').date()
        return True
    except ValueError:
        return False


def get_listings_in_date_range(start_date, end_date):
    unavailable_listings = Listing.objects.filter(
        Q(reservation__start_date__lte=start_date, reservation__end_date__gte=start_date) |
        Q(reservation__start_date__lte=end_date, reservation__end_date__gte=end_date) |
        Q(reservation__start_date__gte=start_date, reservation__end_date__lte=end_date)
    )
    available_listings = Listing.objects.exclude(id__in=unavailable_listings.values_list('id', flat=True))
    return available_listings


def validate_input_dates(start_date, end_date):
    start_date, end_date = parse_dates(start_date,end_date)

    if start_date < datetime.today().date() or end_date < datetime.today().date():
        return {'date error': 'The selected day must not be past date.',}

    if start_date is None or end_date is None:
        return {'start_date': 'is required.', 'end_date': 'is required.'}

    if start_date > end_date:
        return {'error': 'Start date must be before end date.'}

    if not is_valid_date_format(start_date) or not is_valid_date_format(end_date):
        return {'error': 'Invalid date format. Please use the format "YYYY-MM-DD".'}

    return None

def parse_dates(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    return start_date, end_date