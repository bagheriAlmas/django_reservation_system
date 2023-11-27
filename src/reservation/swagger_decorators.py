from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

common_parameters = [
    openapi.Parameter(
        name='start_date',
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        description='Start date for availability search',
    ),
    # Add other common parameters
]

# Define common responses
common_responses = {
    400: 'Bad Request',
    500: 'Internal Server Error',
}

def available_listings_swagger_decorator(func):
    return swagger_auto_schema(
        method='get',
        manual_parameters=common_parameters + [
            # Additional parameters specific to this endpoint
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
            **common_responses,
        },
    )(func)

def add_reservation_swagger_decorator(func):
    return swagger_auto_schema(
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
            **common_responses,
        },
    )(func)
