from collections import OrderedDict
from django.contrib.auth.models import User
from app.models import Product, Order, OrderAction, AppSetting
from time import strptime
from django.utils.datetime_safe import strftime
from app.utility import GlobalOperations, Anonymous
from django.template import Context, Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib2
import urllib
import json
import smtplib
from django.template.loader import render_to_string
import logging

class ProductOperations(object):
    def __init__(self, customer_username, order_type):
        self.customer_username = customer_username
        self.order_type = order_type

    def get_products(self):
        all_products_dict = ()
        dictionary = OrderedDict()
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
                bulk_plan_items = bulk_plan.items.all()
                # generate list of product dictionaries from bulk plan items

                for item in bulk_plan_items:
                    dictionary = OrderedDict()
                    dictionary["id"] = item.product.id                
                    dictionary["name"] = item.product.name
                    dictionary["items_string"] = item.product.items_string
                    dictionary["number_of_items"] = item.product.number_of_items
                    #to get accurate max_allowed for each item, we need to
                    #select all order items in this customer's bulk plans
                    #within current activation period
                    if not item.max_quantity:
                        dictionary["max_allowed"] = item.max_quantity

                    else:
                        number_of_product_used = bulk_plan.get_processed_count_for_product(item.product.id)
                        dictionary["max_allowed"] = item.max_quantity - number_of_product_used

                    all_products_dict += (dictionary,)

                max_pieces = bulk_plan.pieces_left
        #NORMAL
        else:
            all_products = Product.objects.all()

            for product in all_products:
                dictionary = OrderedDict()
                dictionary["id"] = product.id                
                dictionary["name"] = product.name
                dictionary["items_string"] = product.items_string
                dictionary["number_of_items"] = product.number_of_items
                dictionary["price"] = product.price

                all_products_dict += (dictionary,)

        return { "max_pieces": max_pieces, "products": all_products_dict }

    #product: id, name, price, items (id, name, count)
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
            dictionary = OrderedDict()
            dictionary["id"] = product.id                
            dictionary["name"] = product.name
            dictionary["price"] = product.price

            items_list = []
            
            for item in product.items.all():
                item_dict = OrderedDict()
                item_dict["id"] = item.id
                item_dict["name"] = item.name
                item_dict["count"] = item.quantity
                items_list.append(item_dict)

            dictionary["items"] = items_list

            result.append(dictionary)


        return result

class OrderOperations(object):
    @staticmethod
    def generate_order_number(order):
        '''
        datetime(yymmddhhmm)+customer_id(three_padded)+N_or_B
        '''
        date_component = order.date_initiated.strftime("%y%m%d%H%M")
        zero_padded_customer_id = "{0:03d}".format(order.customer.id)
        order_number = '{0}{1}{2}'.format(date_component, zero_padded_customer_id, order.type,)

        return order_number

    @staticmethod
    def generate_item_tag(order_number, product_serial, item_serial):
        '''
        item tag consists of order_number__product_serial__item_serial
        '''
        return '{0}/{1:03d}/{2:02d}'.format(order_number, product_serial, item_serial)

    @staticmethod
    def get_order_details(order_id):
        order = Order.objects.get_or_none(id=order_id)
        dictionary = OrderedDict()

        if not order:
            pass

        else:
            dictionary["order_number"] = order.order_number
            dictionary["customer"] = { "username": order.customer.username, "full_name": order.customer.profile.full_name}
            dictionary["staff"] = { "username": order.attendant_staff.username }

            order_type_choice_dict = dict(order.ORDER_TYPE_CHOICE)
            dictionary["type"] = order_type_choice_dict[order.type]

            order_status_dict = dict(order.ORDER_STATUS_CHOICE)
            dictionary["status"] = order_status_dict[order.status]

            dictionary["number_of_items"] = order.number_of_items
            dictionary["date_received"] = GlobalOperations.get_date_as_text(order.date_initiated, True)
            dictionary["date_fulfillment_scheduled"] = GlobalOperations.get_date_as_text(order.date_fulfillment_scheduled, False)
            dictionary["date_fulfillment_actual"] = GlobalOperations.get_date_as_text(order.date_fulfillment_actual, False)
            dictionary["date_delivered"] = GlobalOperations.get_date_as_text(order.date_delivered, False)
            dictionary["payment_status"] = order.payment_status
            dictionary["amount_payable"] = order.amount_payable
            dictionary["amount_paid"] = order.amount_paid

            order_items = order.items
            items_output = []
            for item in order_items:
                item_dict = OrderedDict()
                item_dict["name"] = item.item_name
                item_dict["product"] = item.order_product.product_name
                item_dict["colour"] = item.colour.name
                item_dict["alteration"] = item.alteration.name if item.alteration else "None"
                item_dict["tag"] = item.item_tag 
                items_output.append(item_dict)
                    
            dictionary["items"] = items_output #modify to pick out relevants fields from order_items to create a list of order_items
        
            order_payments = order.payments
            payments_output = []
            for order_payment in order_payments:
                payment_dict = OrderedDict()
                payment_dict["amount"] = order_payment.payment.amount
                payment_dict["instrument"] = order_payment.payment.instrument_text
                payment_dict["reference"] = order_payment.payment.reference
                payment_dict["cashier"] = order_payment.payment.cashier.username
                payment_dict["date"] = GlobalOperations.get_date_as_text(order_payment.payment.date, True)
                payments_output.append(payment_dict)

            dictionary["payments"] = payments_output

        return dictionary

    @staticmethod
    def update_order_status(order, new_order_status, order_action, user):
        order.status = new_order_status
        order.save()
                
        action = OrderAction(order=order, action=order_action, actor=user,)
        action.save()

class Notifications(object):
    @staticmethod
    def generate_email(template_file_path, context_dictionary):
        #our weird character for templating would be ~, of course
        email_text = render_to_string(template_file_path, context_dictionary,)
        return email_text

    @staticmethod
    def send_email(html, subject, recipient):
        sent = False
        error = ''

        try:
            from_name = AppSetting.objects.get(name='smtp_sender_name',).value
            from_addr = AppSetting.objects.get(name='smtp_sender_address',).value
            from_address = "{0} <{1}>".format(from_name, from_addr,)
            
            email_host = AppSetting.objects.get(name='smtp_host',).value
            email_port = int(AppSetting.objects.get(name='smtp_port',).value)
            email_username = AppSetting.objects.get(name='smtp_username',).value
            email_password = AppSetting.objects.get(name='smtp_password',).value
            email_use_ssl = AppSetting.objects.get(name='smtp_use_ssl',).value
        
            msg = MIMEMultipart()
            msg['From'] = from_address
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(html,'html',),)

            mailserver = smtplib.SMTP(email_host, email_port,)
            mailserver.ehlo()

            if bool(email_use_ssl):
                mailserver.starttls()

            mailserver.ehlo()
            mailserver.login(email_username, email_password,)
            mailserver.sendmail(from_address, recipient, msg.as_string(),)
            mailserver.quit()

            sent = True

        except Exception, exc:
            error = "mail failed; {0}".format(str(exc),)
            logging.error(error,)
            raise

        return {'sent': sent, 'error': error,}

    @staticmethod
    def send_smssolutions_sms(template_file_path, context_dictionary, recipient, header=None):         
        sent = False
        error = ''
        try:       
            message = render_to_string(template_file_path, context_dictionary,)         
            data = {}
            data['username'] = AppSetting.objects.get(name='sms_api_username',).value
            data['password'] = AppSetting.objects.get(name='sms_api_password',).value
            data['header'] = header if header else AppSetting.objects.get(name='sms_api_sender',).value    
            data['destAddr'] = recipient
            data['message'] = message
            url_values = urllib.urlencode(data)
        
            url = AppSetting.objects.get(name='sms_api_url',).value
            full_url = url + '?' + url_values
            data = urllib2.urlopen(full_url)

            if data.read().lower() == 'sms sent':
                sent = True

            else:
                error = 'data'

        except Exception, exc:
            exception_msg = str(exc)
            error = "mail failed; {0}".format(exception_msg,)
            logging.error(error,)
            raise

        return {'sent': sent, 'error': error,}

class General(object):
    @staticmethod
    def get_company_information():
        laundry_name = AppSetting.objects.get(name='laundry_name',).value
        laundry_address = AppSetting.objects.get(name='laundry_address',).value
        laundry_phone = AppSetting.objects.get(name='laundry_phone',).value
        laundry_email = AppSetting.objects.get(name='laundry_email',).value
        return Anonymous(name = laundry_name, address = laundry_address, phone = laundry_phone, email = laundry_email)



