from django.contrib.auth.models import User
from .utils import available_listings_in_date_range_query
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Listing, Reservation
from .serializers import ListingSerializer
from datetime import datetime, timedelta


class ShowAllListingsTestCase(APITestCase):
    def setUp(self):
        # Create a user for the owner field
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some sample listings for testing and associate them with the user
        Listing.objects.create(owner=self.user, name='Listing 1', address='Address 1', description='Description 1')
        Listing.objects.create(owner=self.user, name='Listing 2', address='Address 2', description='Description 2')
        # ...

    def test_show_all_listings(self):
        # Login the user (assuming you have authentication in place)
        self.client.login(username='testuser', password='testpassword')

        # Define the URL for the API endpoint
        url = reverse('listing-list')

        # Make a GET request to the endpoint
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains the correct number of listings
        self.assertEqual(len(response.data['results']), 2)  # Adjust the number based on your sample data

        # Optionally, you can further check the structure of the response data
        # For example, if you have a serializer for the Listing model:
        listings = Listing.objects.all()
        serializer = ListingSerializer(listings, many=True)
        self.assertEqual(response.data['results'], serializer.data)


class ShowAllAvailableListingsTestCase(APITestCase):
    def setUp(self):
        # Create a user for the owner field
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some sample listings for testing and associate them with the user
        Listing.objects.create(owner=self.user, name='Listing 1', address='Address 1', description='Description 1')
        Listing.objects.create(owner=self.user, name='Listing 2', address='Address 2', description='Description 2')

    def test_show_all_available_listings(self):
        # Set up input data for testing
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        input_data = {"start_date": str(start_date), "end_date": str(end_date)}

        # Define the URL for the API endpoint
        url = reverse('available-listing-list')

        # Make a POST request to the endpoint with input data in the request body
        response = self.client.get(url, data=input_data)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Optionally, you can further check the structure of the response data
        # For example, if you have a serializer for the Listing model:
        available_listings = available_listings_in_date_range_query(start_date, end_date)

        serializer = ListingSerializer(available_listings, many=True)

        self.assertEqual(response.data['results'], serializer.data)

    def test_show_all_available_listings_invalid_input(self):
        # Set up invalid input data for testing
        invalid_input_data = {'start_date': 'invalid_date', 'end_date': 'invalid_date'}

        # Define the URL for the API endpoint
        url = reverse('available-listing-list')

        # Make a GET request to the endpoint with invalid input data
        response = self.client.get(url, data=invalid_input_data)

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Optionally, you can further check the structure of the response data for error messages
        self.assertIn('start_date', response.data)
        self.assertIn('end_date', response.data)


class AddReservationTestCase(APITestCase):
    def setUp(self):
        # Create a user for the owner field
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create a sample listing for testing and associate it with the user
        self.listing = Listing.objects.create(
            owner=self.user,
            name='Sample Listing',
            address='Sample Address',
            description='Sample Description'
        )

    def test_add_reservation(self):
        # Login the user (assuming you have authentication in place)
        self.client.login(username='testuser', password='testpassword')

        # Set up input data for testing
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        input_data = {
            'listing': self.listing.id,
            'name': 'Mahdi Bagheri',
            'start_date': str(start_date),
            'end_date': str(end_date)
        }

        # Define the URL for the API endpoint
        url = reverse('add-reservation')

        # Make a POST request to the endpoint with input data
        response = self.client.post(url, data=input_data, format='json')

        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Optionally, you can further check the structure of the response data
        # For example, if you have a serializer for the Reservation model:
        from reservation.serializers import ReservationSerializer
        reservation = Reservation.objects.get(id=response.data['id'])
        serializer = ReservationSerializer(reservation)

        self.assertEqual(response.data, serializer.data)
