import logging
from django.core.cache import cache
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, get_object_or_404
from rest_framework.response import Response
from reservation.models import Listing
from reservation.serializers import ReservationSerializer, ListingSerializer
from reservation.swagger_decorators import available_listings_swagger_decorator, add_reservation_swagger_decorator
from reservation.utils import (parse_input_dates, available_listings_in_date_range_query,
                               listing_serializers_paginate_response, listing_paginated_items)

logger = logging.getLogger(__name__)

class ShowAllListingsView(ListAPIView):
    queryset = Listing.objects.all().select_related('owner')
    serializer_class = ListingSerializer

    def list(self, request, *args, **kwargs):
        response = listing_serializers_paginate_response(request, self.get_queryset())
        logger.info('ShowAllListingsView executed successfully')
        return response

class ShowAllAvailableListingsView(ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        try:
            start_date, end_date = parse_input_dates(self.request.query_params.get('start_date') or None,
                                                     self.request.query_params.get('end_date') or None)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        return available_listings_in_date_range_query(start_date, end_date)

    def list(self, request, *args, **kwargs):
        response = listing_serializers_paginate_response(request, self.get_queryset())
        logger.info('ShowAllAvailableListingsView executed successfully')
        return response

class AddReservationView(CreateAPIView):
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        listing = get_object_or_404(Listing, pk=listing_id)

        try:
            start_date, end_date = parse_input_dates(request.data.get('start_date') or None,
                                                     request.data.get('end_date') or None)
        except ValidationError as e:
            logger.info('Input dates have incorrect format')
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        available_listings = available_listings_in_date_range_query(start_date, end_date)
        if listing.id not in available_listings.values_list('id', flat=True):
            logger.info('Failed to Reservation')
            return Response({'error': f'Listing not available for reservation until {end_date}.'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(listing_id)
            logger.info('Reserved successfully')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OverviewReportsView(ListAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def list(self, request, *args, **kwargs):
        paginated_listings = listing_paginated_items(request, self.get_queryset())
        logger.info('OverviewReportsView executed successfully')
        return render(request, 'pages/listings_report.html', {"listings": paginated_listings})

class ListingDetailsView(ListAPIView):
    serializer_class = ListingSerializer

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if cache.get(pk):
            listing = cache.get(pk)
            logger.info('Load data from cache')
        else:
            listing = get_object_or_404(Listing, pk=pk)
            cache.set(pk, listing)
            logger.info('Load data from db')

        reservations = listing.reservations.all()
        paginated_reservations = listing_paginated_items(request, reservations)

        context = {
            'listings': listing,
            'reservations_page': paginated_reservations,
        }

        logger.info('ListingDetailsView executed successfully')
        return render(request, 'pages/listing_details.html', context)
