from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from reservation.models import Listing
from reservation.serializers import ListingSerializer, ReservationSerializer
from reservation.swagger_decorators import available_listings_swagger_decorator, add_reservation_swagger_decorator
from reservation.utils import parse_input_dates, available_listings_in_date_range_query


def listing_serializers_paginate_response(request, queryset):
    paginator = PageNumberPagination()
    try:
        paginated_listings = paginator.paginate_queryset(queryset, request)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    serializer = ListingSerializer(paginated_listings, many=True)
    return paginator.get_paginated_response(serializer.data)


def listing_paginated_items(request, queryset):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 10)

    try:
        paginated_items = paginator.page(page)
    except PageNotAnInteger:
        paginated_items = paginator.page(1)
    except EmptyPage:
        paginated_items = paginator.page(paginator.num_pages)
    return paginated_items


@api_view(['GET'])
def show_all_listings(request):
    listings = Listing.objects.all()
    response = listing_serializers_paginate_response(request, listings)
    return response


@available_listings_swagger_decorator
@api_view(['GET'])
def show_all_available_listings(request):
    try:
        start_date, end_date = parse_input_dates(request.query_params.get('start_date') or None,
                                                 request.query_params.get('end_date') or None)
    except ValidationError as e:
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    listings_queries = available_listings_in_date_range_query(start_date, end_date)
    response = listing_serializers_paginate_response(request, listings_queries)
    return response


@add_reservation_swagger_decorator
@api_view(['POST'])
def add_reservation(request):
    listing_id, start_date, end_date = request.data.get('listing'), request.data.get('start_date'), request.data.get(
        'end_date')
    listing = get_object_or_404(Listing, pk=listing_id)

    try:
        start_date, end_date = parse_input_dates(request.query_params.get('start_date') or None,
                                                 request.query_params.get('end_date') or None)
    except ValidationError as e:
        return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    available_listings = available_listings_in_date_range_query(start_date, end_date)
    if not listing.id in available_listings.values_list('id', flat=True):
        return Response({'error': f'Listing not available for reservation until {end_date}.'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = ReservationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def overview_reports(request):
    listings = Listing.objects.all()
    paginated_listings = listing_paginated_items(request, listings)
    return render(request, 'pages/listings_report.html', {"listings": paginated_listings})


@api_view(['GET'])
def listing_details(request, pk):
    listings = Listing.objects.get(pk=pk)

    reservations = listings.reservations.all()
    paginated_reservations = listing_paginated_items(request, reservations)

    context = {
        'listings': listings,
        'reservations_page': paginated_reservations,
    }
    return render(request, 'pages/listing_details.html', context)
