#from django.contrib.auth.models import User
from app.models import UserProfile, Product
from rest_framework import serializers

class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'full_name', 'email')

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    #id: '1',
    #name: 'Teabag',
    #items: 'Rope, leaves and paper bag',
    #numberOfItems: 2,
    #price: 500.03,
    #maxAllowed: null //only for bulk
    class Meta:
        model = Product
        fields = ('id', 'name', 'items_string', 'number_of_items', 'price')



