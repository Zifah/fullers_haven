from django.contrib.auth.models import User
from rest_framework import viewsets, status
from app.serializers import CustomerSerializer, ColourSerializer, AlterationSerializer
from app.models import UserProfile, Product, Colour, Alteration, Order, BulkPlan, OrderProduct, OrderItem, Item, ProductItem, OrderAction
from rest_framework.views import APIView
from rest_framework.response import Response
import json
from app.operations import ProductOperations, OrderOperations, Notifications, General
from datetime import datetime
from decimal import Decimal
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from app.utility import Anonymous, GlobalOperations
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging

'''
Viewsets
'''
class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows customers to be viewed or edited
    """
    queryset = UserProfile.objects.filter(user__is_staff=False)
    serializer_class = CustomerSerializer

class ColourViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows colours to be viewed
    """
    queryset = Colour.objects.all()
    serializer_class = ColourSerializer

class AlterationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows colours to be viewed
    """
    queryset = Alteration.objects.all()
    serializer_class = AlterationSerializer

'''
API Views
'''
class ProductView(APIView):
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

class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('pk', None)
        order = Order.objects.get_or_none(id=order_id)

        if order_id and order:
            order = OrderOperations.get_order_details(order_id)
            response = Response(order, status=status.HTTP_200_OK)

        else:
            response = Response({"error": "Order not found!"}, status=status.HTTP_404_NOT_FOUND)

        return response

    def post(self, request, *args, **kwargs):
        complete_json_order = request.body

        complete_order_dict = json.loads(complete_json_order)

        customer_username = complete_order_dict["customer"]
        order_type = complete_order_dict["type"]
        product_items = complete_order_dict["productItems"]
        products_id_quantity = complete_order_dict["products"]
        date_fulfillment_scheduled = complete_order_dict["dateFulfilmentScheduled"]
        #dateFulfilmentScheduled

        order = Order()
        order.customer = User.objects.get(username=customer_username)
        order.date_initiated = datetime.now()
        order.date_fulfillment_scheduled = datetime.strptime(date_fulfillment_scheduled, '%d/%m/%Y')
        order.attendant_staff = request.user
        order.type = order_type

        if order.type == 'B':
            order.bulk_plan = BulkPlan.objects.get(owner__username=customer_username)

        if order.type == 'N':
            #calculate order price
            total_price = Decimal(0.0)
            for product in products_id_quantity:
                price = Product.objects.get(id=product["id"]).price
                total_this_product = price * product["quantity"]
                total_price += total_this_product

            order.amount = total_price
            order.amount_discount = 0
            order.amount_payable = order.amount - order.amount_discount

        order.order_number = OrderOperations.generate_order_number(order)
        order.save()

        action = OrderAction(order=order, action='C', actor=request.user,)
        action.save()

        # create order products
        for product in product_items:
            product_id = product["id"]
            product_serial = product["serialNumber"]
            product_items = product["items"]

            order_product = OrderProduct(order=order)
            order_product.product = Product.objects.get(id=product_id)
            order_product.serial_number = product_serial
            order_product.product_name = order_product.product.name
            order_product.product_price = order_product.product.price

            order_product.save()

            # create and add orderitems to order product
            for item in product_items:
                item_serial = item["serialNumber"]
                item_id = item["id"]
                item_colour_id = item["colourId"]
                item_alteration_id = item["alterationId"]

                item_model = ProductItem.objects.get(id=item_id).item

                order_item = OrderItem(order_product=order_product, serial_number=item_serial, item=item_model,)

                if item_colour_id:
                    order_item.colour = Colour.objects.get(id=item_colour_id)

                if item_alteration_id:
                    order_item.alteration = Alteration.objects.get(id=item_alteration_id)
                
                order_item.item_name = item_model.name
                order_item.item_tag = OrderOperations.generate_item_tag(order.order_number, product_serial, item_serial)

                order_item.save()
        
        # send order email
        to_email = order.customer.email
        logging.error(to_email,)
        if to_email:
            context_dictionary = dict()

            context_dictionary['company'] = General.get_company_information()
            context_dictionary['order'] = order

            invoice_email = Notifications.generate_email('invoice.htm', context_dictionary)
            response = Notifications.send_email(invoice_email, "New Fullers Haven Order", to_email,) 

        # send order SMS
        to_phone = order.customer.profile.phone if order.customer.profile else None
        logging.error(to_phone,)

        if to_phone:
            context_data = {'order_number': order.order_number, 
                            'number_of_items': order.number_of_items, 
                            'collection_date': GlobalOperations.get_date_as_text(order.date_fulfillment_scheduled, False)
                            }
            response = Notifications.send_smssolutions_sms('sms/new_order.txt', context_data, "234{0}".format(to_phone[1:]),)

        logging.debug("Good boy",)
        return Response({'order_id' : order.id}, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        modified_order_json = request.body
        modified_order_dict = json.loads(modified_order_json)

        new_order_status = modified_order_dict["status"];
        
        order_id = self.kwargs.get('pk', None)
        order = Order.objects.get_or_none(id=order_id)

        if order:
            if new_order_status == "Cancelled" and order.status == 'P':
                OrderOperations.update_order_status(order, 'C', 'X', request.user)
                #TODO: Notify customer of order cancellation

            elif new_order_status == "Fulfilled" and order.status == 'P':
                order.date_fulfillment_actual = datetime.now()                
                OrderOperations.update_order_status(order, 'F', 'F', request.user)
                #TODO: Notify customer of order fulfillment and invite to pick up

            elif new_order_status == "Delivered" and order.status == 'F':
                order.date_delivered = datetime.now()
                OrderOperations.update_order_status(order, 'D', 'D', request.user)
                #TODO: Notify customer of order delivery/collection

            else:
                #TODO: kindly do nothing
                pass

            response = Response(OrderOperations.get_order_details(order_id), status=status.HTTP_200_OK)

        else:
            response = Response({"error": "Order not found!"}, status=status.HTTP_404_NOT_FOUND)

        return response

'''
Template views
'''
class OrderInvoiceView(DetailView):
    template_name = 'invoice.htm'
    context_object_name = "order"
    model = Order

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(OrderInvoiceView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['company'] = General.get_company_information()
        return context

    @method_decorator(login_required(login_url='/admin'))
    def dispatch(self, *args, **kwargs):
        return super(OrderInvoiceView, self).dispatch(*args, **kwargs)

class OrderTagsView(DetailView):
    template_name = 'order_item_tags.htm'
    context_object_name = "order"
    model = Order

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(OrderTagsView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        order = context['order']
        tags_per_row = 6
        #number_of_items = order.items.count()        
        #number_of_rows = int(number_of_items / tags_per_row)

        #if number_of_items % tags_per_row != 0:
           # number_of_rows += 1;

        #number_of_rows = range(number_of_rows)
        #tags_per_row = range(tags_per_row)

        context['tags_per_row'] = tags_per_row
        #context['number_of_rows'] = number_of_rows
        return context

    @method_decorator(login_required(login_url='/admin'))
    def dispatch(self, *args, **kwargs):
        return super(OrderTagsView, self).dispatch(*args, **kwargs)



            