from django.contrib.auth.models import User
from rest_framework import viewsets
from app.serializers import CustomerSerializer
from app.models import UserProfile, Product
from collections import OrderedDict


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
            # get the customer's bulk plan
            bulk_plan = customer.bulk_plan
            # get the bulk plan items
            bulk_plan_items = bulk_plan.items
            # generate list of product dictionaries from bulk plan items

            for item in bulk_plan_items:
                dict["id"] = item.product.id                
                dict["name"] = item.product.name
                dict["items_string"] = item.product.items_string
                dict["number_of_items"] = item.product.number_of_items
                #to get max_allowed for each item, we need to select all order items in this customer's bulk plans within current activation period
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
                dict["id"] = product.id                
                dict["name"] = product.name
                dict["items_string"] = product.items_string
                dict["number_of_items"] = product.number_of_items
                dict["price"] = product.price

                all_products_dict += (dict,)

        return { "max_pieces": max_pieces, "products": all_products_dict }
            


class ProductsView(APIView):
    def get(self, request, *args, **kw):
        customer_username = request.GET.get('customer', None)
        order_type = request.GET.get('order_type', None)

        # Any URL parameters get passed in **kw
        myClass = ProductOperations(get_arg1, get_arg2,)
        result = myClass.get_products()
        response = Response(result, status=status.HTTP_200_OK)
        return response


            