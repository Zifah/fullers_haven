from django.contrib.auth.models import User
from rest_framework import viewsets, status
from app.serializers import CustomerSerializer
from app.models import UserProfile, Product
from collections import OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response
import json


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = UserProfile.objects.filter(user__is_staff=False)
    serializer_class = CustomerSerializer

class ProductOperations(object):
    def __init__(self, customer_username, order_type):
        self.customer_username = customer_username
        self.order_type = order_type

    def get_products(self):
        all_products_dict = ()
        dict = OrderedDict()
        max_pieces = None
        
        if self.order_type == 'B':
            # get the customer
            customer = User.objects.get(username=self.customer_username)
            bulk_plan = None
            # get the customer's bulk plan
            try:
                bulk_plan = customer.bulk_plan
            # get the bulk plan items
            except:
                pass

            if bulk_plan:
                bulk_plan_items = bulk_plan.items
                # generate list of product dictionaries from bulk plan items

                for item in bulk_plan_items:
                    dict = OrderedDict()
                    dict["id"] = item.product.id                
                    dict["name"] = item.product.name
                    dict["items_string"] = item.product.items_string
                    dict["number_of_items"] = item.product.number_of_items
                    #to get accurate max_allowed for each item, we need to select all order items in this customer's bulk plans within current activation period
                    dict["max_allowed"] = item.max_quantity
            
                    all_products_dict += (dict,)

                max_pieces = bulk_plan.pieces_left
        #NORMAL
        else:
            #id: '1',
            #name: 'Teabag',
            #items: 'Rope, leaves and paper bag',
            #numberOfItems: 2,
            #price: 500.03,
            #maxAllowed: null //only for bulk
            all_products = Product.objects.all()

            for product in all_products:
                dict = OrderedDict()
                dict["id"] = product.id                
                dict["name"] = product.name
                dict["items_string"] = product.items_string
                dict["number_of_items"] = product.number_of_items
                dict["price"] = product.price

                all_products_dict += (dict,)

        return { "max_pieces": max_pieces, "products": all_products_dict }

    #product: id, name, price, items (name, count)
    def get_products_by_id(self, ids):
        '''
        - Convert ids string to python array
        - Get all products with IDs in the list
        - Extract the properties listed above for each object on this list
        - Put the properties into a dictionary
        - Add each dictionary into a list
        - return tuple at end of operation
        '''
        result = []

        ids_list = json.loads(ids)
        matching_products = Product.objects.filter(id__in=ids_list)

        for product in matching_products:
            dict = OrderedDict()
            dict["id"] = product.id                
            dict["name"] = product.name
            dict["price"] = product.price

            items_list = []
            
            for item in product.items.all():
                item_dict = OrderedDict()
                item_dict["name"] = item.name
                item_dict["count"] = item.quantity
                items_list.append(item_dict)

            dict["items"] = items_list

            result.append(dict)


        return result
            


class ProductsView(APIView):
    def get(self, request, *args, **kw):
        ids = request.GET.get('ids', None)
        customer_username = request.GET.get('customer', None)
        order_type = request.GET.get('order_type', None)        
        
        myClass = ProductOperations(customer_username, order_type)


        if ids:
            result = myClass.get_products_by_id(ids)
        else:
            result = myClass.get_products()

        response = Response(result, status=status.HTTP_200_OK)
        return response


            