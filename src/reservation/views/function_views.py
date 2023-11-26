from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from reservation.models import Listing
from reservation.serializers import ListingSerializer, ReservationSerializer
from reservation.utils import validate_input_dates, parse_dates, get_listings_in_date_range


@api_view(['GET'])
def show_all_listings(request):
    try:
        paginator = PageNumberPagination()

        listings = Listing.objects.all()
        paginated_listings = paginator.paginate_queryset(listings, request)

        serializer = ListingSerializer(paginated_listings, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='start_date',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            description='Start date for availability search',
        ),
        openapi.Parameter(
            name='end_date',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            description='End date for availability search',
        ),
    ],
    responses={
        200: openapi.Response(
            description='OK',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'next': openapi.Schema(type=openapi.TYPE_STRING),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING),
                    'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                },
            ),
        ),
        400: 'Bad Request',
        500: 'Internal Server Error',
    },
)
@api_view(['GET'])
def show_all_available_listings(request):
    start_date, end_date = request.query_params.get('start_date'), request.query_params.get('end_date')

    error_response = validate_input_dates(start_date, end_date)
    if error_response:
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    start_date, end_date = parse_dates(start_date, end_date)

    try:
        paginator = PageNumberPagination()

        available_listings = get_listings_in_date_range(start_date, end_date)

        paginated_listing = paginator.paginate_queryset(available_listings, request)

        serializer = ListingSerializer(paginated_listing, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'listing': openapi.Schema(type=openapi.TYPE_INTEGER),
            'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        },
        required=['listing', 'start_date', 'end_date'],
    ),
    responses={
        201: 'Created',
        400: 'Bad Request',
    },
)
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
    listings_per_page = 10
    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Paginate the listings
    paginator = Paginator(listings, listings_per_page)
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, 'pages/listings_report.html', {"listings": listings})


@api_view(['GET'])
def listing_details(request, pk):
    listings = Listing.objects.get(pk=pk)
    listings_per_page = 10

    # Get the page number from the request's GET parameters
    page = request.GET.get('page', 1)

    # Create a Paginator object
    paginator = Paginator(listings.reservations.all(), listings_per_page)

    try:
        # Get the specified page
        reservations_page = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        reservations_page = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, show the last page
        reservations_page = paginator.page(paginator.num_pages)

    context = {
        'listings': listings,
        'reservations_page': reservations_page,
    }

    return render(request, 'pages/listing_details.html', context)
