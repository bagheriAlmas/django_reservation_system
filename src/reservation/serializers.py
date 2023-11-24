from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Listing, Reservation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    class Meta:
        model = Listing
        fields = ['id', 'name','address','description','owner']


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"
