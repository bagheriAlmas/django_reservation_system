from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Listing
from .serializers import ListingSerializer, ReservationSerializer
from .utils import validate_input_dates, parse_dates, get_listings_in_date_range


@api_view(['GET'])
def show_all_listings(request):
    try:
        paginator = PageNumberPagination()
        paginator.page_size = 10

        listings = Listing.objects.all()
        paginated_listings = paginator.paginate_queryset(listings, request)

        serializer = ListingSerializer(paginated_listings, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def show_all_available_listing(request):
    start_date, end_date = request.data.get('start_date'), request.data.get('end_date')

    error_response = validate_input_dates(start_date, end_date)
    if error_response:
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    start_date, end_date = parse_dates(start_date, end_date)

    available_listings = get_listings_in_date_range(start_date, end_date)

    serializer = ListingSerializer(available_listings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_reservation(request):
    listing_id, start_date, end_date = request.data.get('listing'), request.data.get('start_date'), request.data.get(
        'end_date')

    listing = get_object_or_404(Listing, pk=listing_id)

    error_response = validate_input_dates(start_date, end_date)
    if error_response:
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    start_date, end_date = parse_dates(start_date, end_date)

    if not is_listing_available_for_reservation(listing, start_date, end_date):
        return Response({'error': f'Listing not available for reservation until {end_date}.'},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def is_listing_available_for_reservation(listing, start_date, end_date):
    available_listings = get_listings_in_date_range(start_date, end_date)
    return listing.id in available_listings.values_list('id', flat=True)

@api_view(['GET'])
def overview_reports(request):
    listings = Listing.objects.all()
    return render(request, 'pages/listings_report.html', {"listings": listings})