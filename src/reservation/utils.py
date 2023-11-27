import logging

from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Listing
from .serializers import ListingSerializer

logger = logging.getLogger(__name__)

def available_listings_in_date_range_query(start_date, end_date):
    unavailable_listings = Listing.objects.filter(
        Q(reservations__start_date__lte=start_date, reservations__end_date__gte=start_date) |
        Q(reservations__start_date__lte=end_date, reservations__end_date__gte=end_date) |
        Q(reservations__start_date__gte=start_date, reservations__end_date__lte=end_date)
    )
    logger.info('Select all reservations between start_date and end_date')

    available_listings = Listing.objects.exclude(id__in=unavailable_listings.values_list('id', flat=True))
    logger.info('Select all reservations not in unavailable_listings')

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


def listing_serializers_paginate_response(request, queryset):
    paginator = PageNumberPagination()
    try:
        paginated_listings = paginator.paginate_queryset(queryset, request)
    except Exception as e:
        logger.info(f' Page Number is Invalid. {str(e)}')
        return Response({'error': 'Invalid page number.'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ListingSerializer(paginated_listings, many=True)
    return paginator.get_paginated_response(serializer.data)


def listing_paginated_items(request, queryset):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)

    try:
        paginated_items = paginator.page(page)
    except PageNotAnInteger:
        logger.info('Invalid page number')
        paginated_items = paginator.page(1)
    except EmptyPage:
        logger.info('Result is an empty page')
        paginated_items = paginator.page(paginator.num_pages)
    return paginated_items
