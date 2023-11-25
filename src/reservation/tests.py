from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Listing
from .serializers import ListingSerializer

class ShowAllListingsTestCase(APITestCase):
    def setUp(self):
        # Create a user for the owner field
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create some sample listings for testing
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
