from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Listing
from .serializers import ListingSerializer


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
