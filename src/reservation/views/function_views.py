import logging

from django.core.cache import cache
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from reservation.models import Listing
from reservation.serializers import ReservationSerializer
from reservation.swagger_decorators import available_listings_swagger_decorator, add_reservation_swagger_decorator
from reservation.utils import (parse_input_dates, available_listings_in_date_range_query,
                               listing_serializers_paginate_response, listing_paginated_items)

logger = logging.getLogger(__name__)

@api_view(['GET'])
def show_all_listings(request):
    """
    Show All Listings List
    """
    listings = Listing.objects.all().select_related('owner')
    response = listing_serializers_paginate_response(request, listings)
    return response


@available_listings_swagger_decorator
@api_view(['GET'])
def show_all_available_listings(request):
    """
    Show Available Listings Between Two Ranges of Date
    start_date and end_date sets as a query parameters
    """
    try:
        start_date, end_date = parse_input_dates(request.query_params.get('start_date'),
                                                 request.query_params.get('end_date'))
    except ValidationError as e:
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)

    listings_queries = available_listings_in_date_range_query(start_date, end_date)
    response = listing_serializers_paginate_response(request, listings_queries)
    logger.info('show_all_available_listings executed successfully')
    return response


@add_reservation_swagger_decorator
@api_view(['POST'])
def add_reservation(request):
    """
    Add listing reservation
    Customers can check available rooms between two dates and reserve them
    listing_id, customer_name, start_date, and end_date are filled in request body
    """
    listing_id = request.data.get('listing')
    listing = get_object_or_404(Listing, pk=listing_id)

    try:
        start_date, end_date = parse_input_dates(request.data.get('start_date'),
                                                 request.data.get('end_date'))
    except ValidationError as e:
        logger.info('Input dates has not correct format')
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)

    available_listings = available_listings_in_date_range_query(start_date, end_date)
    if not listing.id in available_listings.values_list('id', flat=True):
        return Response({'error': f'Listing not available for reservation until {end_date}.'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        cache.delete(listing_id)
        logger.info(f'Listing id: {listing_id}, Added new reservation.')

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        logger.info(f'Listing id: {listing_id}, Failed to add new reservation.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def overview_reports(request):
    listings = Listing.objects.all()
    paginated_listings = listing_paginated_items(request, listings)
    logger.info('Report fetch successfully.')
    return render(request, 'pages/listings_report.html', {"listings": paginated_listings})


@api_view(['GET'])
def listing_details(request, pk):
    if cache.get(pk):
        listing = cache.get(pk)
    else:
        listing = get_object_or_404(Listing, pk=pk)
        cache.set(pk, listing)

    reservations = listing.reservations.all()
    paginated_reservations = listing_paginated_items(request, reservations)

    context = {
        'listings': listing,
        'reservations_page': paginated_reservations,
    }

    logger.info(f'Listing: {pk}, Report fetch successfully.')
    return render(request, 'pages/listing_details.html', context)
