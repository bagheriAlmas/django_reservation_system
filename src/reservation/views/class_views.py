from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from rest_framework import generics, mixins, pagination, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from ..models import Listing
from ..serializers import ListingSerializer, ReservationSerializer
from ..utils import validate_input_dates, parse_dates, get_listings_in_date_range


class ShowAllListings(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ShowAllAvailableListings(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        error_response = validate_input_dates(start_date, end_date)
        if error_response:
            raise serializers.ValidationError(detail=error_response)
        start_date, end_date = parse_dates(start_date, end_date)
        return get_listings_in_date_range(start_date, end_date)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AddReservationView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Listing.objects.all()
    serializer_class = ReservationSerializer

    def post(self, request, *args, **kwargs):
        listing_id, start_date, end_date = request.data.get('listing'), request.data.get(
            'start_date'), request.data.get('end_date')

        listing = get_object_or_404(Listing, pk=listing_id)

        error_response = validate_input_dates(start_date, end_date)
        if error_response:
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        start_date, end_date = parse_dates(start_date, end_date)

        if not is_listing_available_for_reservation(listing, start_date, end_date):
            return Response({'error': f'Listing not available for reservation until {end_date}.'},
                            status=status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)


def is_listing_available_for_reservation(listing, start_date, end_date):
    available_listings = get_listings_in_date_range(start_date, end_date)
    return listing.id in available_listings.values_list('id', flat=True)


class OverviewReportsView(View):
    template_name = 'pages/listings_report.html'
    items_per_page = 10

    def get_context_data(self, page):
        queryset = Listing.objects.all().select_related("owner")
        paginator = Paginator(queryset, self.items_per_page)

        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            listings = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            listings = paginator.page(paginator.num_pages)

        return {'listings': listings}

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        context = self.get_context_data(page)
        return render(request, self.template_name, context)


class ListingDetailsView(ListView):
    model = Listing
    template_name = 'pages/listing_details.html'
    context_object_name = 'listings'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the page number from the request's GET parameters
        page = self.request.GET.get('page', 1)

        # Create a Paginator object
        paginator = Paginator(context['listings'].reservations.all(), self.paginate_by)

        try:
            # Get the specified page
            reservations_page = paginator.page(page)
        except PageNotAnInteger:
            # If the page parameter is not an integer, show the first page
            reservations_page = paginator.page(1)
        except EmptyPage:
            # If the page is out of range, show the last page
            reservations_page = paginator.page(paginator.num_pages)

        context['reservations_page'] = reservations_page
        return context


listing_details_view = ListingDetailsView.as_view()
