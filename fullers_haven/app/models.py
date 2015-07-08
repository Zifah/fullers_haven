from django.db import models
from django.contrib.auth.models import User
from dateutil import parser
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models.query_utils import Q

# Create your models here.
MONTH_CHOICE = ((1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),)

class ModelWithStatus(models.Model):
    """
    A model that has a status: active or inactive
    """
    STATUS_CHOICE = ((0, 'Inactive'),
    (1, 'Active'),)
    status = models.CharField(max_length=1, choices=STATUS_CHOICE)

    class Meta:
        abstract = True

class UserProfile(models.Model):
    '''
    Fields: user, phone, home_address, work_address
    '''
    user = models.OneToOneField(User, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    ### addresses are being collected for possible future need of using this
    ### data to ask users for transport directions
    home_address = models.CharField(max_length=255, blank=True, null=True)
    work_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

class ItemCategory(ModelWithStatus):
    name = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Item Categories"

class Item(ModelWithStatus):
    name = models.CharField(max_length=50, unique=True,)
    price = models.DecimalField(max_digits=8, decimal_places=2,)
    #code = models.CharField(max_length=3, blank=True, null=True)
    category = models.ForeignKey(ItemCategory, related_name="items", blank=True, null=True)

    def __str__(self):
        return self.name

class Product(ModelWithStatus):
    PRODUCT_TYPE_CHOICE = (('A', 'Automatic'),
    ('M', 'Manual'),)

    name = models.CharField(max_length=50, unique=True,)
    type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICE,)
    price = models.DecimalField(max_digits=8, decimal_places=2,)
    #code = models.CharField(max_length=3, blank=True, null=True)

    def _get_item_names(self):
        names = ""
        for item in self.items.all():
            names += "{0},{1}".format(names, item.name)
        return names.strip(',')

    def __str__(self):
        return self.name

    item_names = property(_get_item_names)

class ProductItem(models.Model):
    product = models.ForeignKey(Product, related_name="items")
    item = models.ForeignKey(Item,)
    quantity = models.PositiveSmallIntegerField()

    def _get_name(self):
        return self.item.name

    def __str__(self):
        return "{0} piece(s) of {1} in product: {2}".format(self.quantity, self.item.name, self.product.name)

    name = property(_get_name)

class Discount(ModelWithStatus):
    name = models.CharField(max_length=50, unique=True,)
    percentage = models.DecimalField(max_digits=5, decimal_places=2,)
    amount = models.DecimalField(max_digits=8, decimal_places=2,)

    def __str__(self):
        return self.name

class Alteration(ModelWithStatus):
    name = models.CharField(max_length=50, unique=True,)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Colour(ModelWithStatus):
    name = models.CharField(max_length=30, unique=True,)

    def __str__(self):
        return self.name

class BulkPlan(models.Model):    
    '''
    - Status is expired if:
	- The current month >= Latest bulk plan activation month + no. of months bulk plan valid or current month is less than latest activation month
    '''
        
    def _get_latest_activation_date(self):
        if not self.activations.all().count():
            return date.min

        latest_activation = self.activations.latest()


        latest_activation_month = int(latest_activation.month)
        latest_activation_year = latest_activation.date_activated.year

        activation_date = date(latest_activation_year, latest_activation_month, 1)
        return activation_date

    def _get_latest_expiration_date(self):
        latest_activation_date = self.latest_activation_date        
        latest_expiration_date = latest_activation_date + relativedelta(months=self.number_of_months_valid)
        return latest_expiration_date
    
    def _is_plan_active(self):
        current_month_year = date(date.today().year, date.today().month, 1)

        #is_active = current_month_year >= activation_month_year and
        #current_month_year < expiration_month_year
        is_active = current_month_year >= self.latest_activation_date and current_month_year < self.latest_expiration_date

        return is_active

    def _get_status(self):        
        return "Active" if self.is_active else "Expired"    

    def _get_no_of_items_processed(self):
    #get all of the customer's bulk orders greater than or equal to first date of month of current activation period
        no_of_orders = Order.objects.all().filter(Q(date_initiated__gte = self.latest_activation_date), 
                                                  Q(customer = self.owner),
                                                  Q(date_initiated__lt = self.latest_expiration_date), 
                                                  Q(type = 'B'),
                                                  ~Q(status = 'C')).count()
        #self.owner.my_orders.all().filter(Q(date_initiated >= latest_activation_date),
        #                                           Q(date_initiated < latest_expiration_date),
        #                                           Q(type = 'B'),
        #                                           ~Q(status = 'C')).count()
        return no_of_orders

    def _get_no_of_items_left(self):
        total_available = self.number_of_items if self.is_active else 0
        return total_available - self.pieces_used

    def __str__(self):
        return "Bulk plan for {0}.".format(self.owner)

    owner = models.OneToOneField(User, related_name="bulk_plan")
    price = models.DecimalField(max_digits=8, decimal_places=2,)
    number_of_items = models.PositiveSmallIntegerField(verbose_name="Total pieces")
    number_of_months_valid = models.PositiveSmallIntegerField()

    is_active = property(_is_plan_active)
    status = property(_get_status)
    name = property(__str__)
    latest_activation_date = property(_get_latest_activation_date)
    latest_expiration_date = property(_get_latest_expiration_date)
    pieces_used = property(_get_no_of_items_processed)
    pieces_left = property(_get_no_of_items_left)

class BulkPlanItem(models.Model):
    bulk_plan = models.ForeignKey(BulkPlan, related_name="items")
    product = models.ForeignKey(Product,)
    max_quantity = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Max. quantity")

    def __str__(self):
        return self.product.name

class BulkPlanActivation(models.Model):
    bulk_plan = models.ForeignKey(BulkPlan, related_name="activations")
    date_activated = models.DateTimeField(auto_now_add=True)
    activated_by = models.ForeignKey(User,)
    month = models.PositiveSmallIntegerField(max_length=1, choices=MONTH_CHOICE)

    def __str__(self):
        return "{0} {1} activation for {2}".format(MONTH_CHOICE[self.month - 1][1], self.date_activated.year, self.bulk_plan)

    class Meta:
        get_latest_by = 'date_activated'

    name = property(__str__)

class Order(models.Model):
    ORDER_TYPE_CHOICE = (('N', 'Normal'),
    ('B', 'Bulk'),)

    ORDER_STATUS_CHOICE = (('C', 'Cancelled'),
    ('P', 'Processing'),
    ('F', 'Fulfilled'),
    ('D', 'Delivered'),)

    order_number = models.CharField(max_length=20, unique=True,)

    date_initiated = models.DateTimeField(auto_now_add=True,)

    '''date order is scheduled to be picked up'''
    date_fulfillment_scheduled = models.DateTimeField()

    '''date when the order became ready for pickup'''
    date_fulfillment_actual = models.DateTimeField()

    '''date when the completed order was received by the customer'''
    date_delivered = models.DateTimeField()

    customer = models.ForeignKey(User, related_name='my_orders')

    attendant_staff = models.ForeignKey(User, related_name='orders_received_by')
    
    type = models.CharField(max_length=1, choices=ORDER_TYPE_CHOICE)

    bulk_plan = models.ForeignKey(BulkPlan, blank=True, null=True)

    ''' not required in bulk orders '''
    amount = models.DecimalField(max_digits=10, decimal_places=2,                                  
                                          blank=True, null=True)
    ''' not required in bulk orders '''
    amount_discount = models.DecimalField(max_digits=10, decimal_places=2, 
                                          blank=True, null=True)
    ''' not required in bulk orders '''
    amount_payable = models.DecimalField(max_digits=10, decimal_places=2, 
                                          blank=True, null=True)

    discount = models.ForeignKey(Discount, blank=True, null=True)

    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICE)

    comments = models.TextField()

    def __str__(self):
        return "{0}'s {1} order; {2}.".format(self.customer, self.type, self.date_collected)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items")
    item = models.ForeignKey(Item,)
    product = models.ForeignKey(Product, related_name="products")
    ''' previously wanted to call this: Product number '''
    serial_number = models.PositiveSmallIntegerField()
    ''' the name of the item as at the creation time of this order '''
    item_name = models.CharField(max_length=50,)
    ''' the name of the product as at the creation time of this order '''
    product_name = models.CharField(max_length=50,)
    '''each item row bears the price of the container product'''
    product_price = models.DecimalField(max_digits=8, decimal_places=2,)
    colour = models.ForeignKey(Colour,)
    ''' 
    either alteration or alteration_text is filled; both cannot be filled
    at the same time
    '''
    alteration = models.ForeignKey(Alteration, blank=True, null=True)
    alteration_text = models.CharField(max_length=255, blank=True, null=True)
    
    item_tag = models.CharField(max_length=10, unique=True)

class OrderAction(models.Model):
    ORDER_ACTION_CHOICE = (('C', 'Creation'),
    ('F', 'Fulfilment'),
    ('X', 'Cancellation'),
    ('D', 'Delivery/Pick-up'),)

    order = models.ForeignKey(Order, related_name="actions")
    action = models.CharField(max_length=1, choices=ORDER_ACTION_CHOICE)
    actor = models.ForeignKey(User,)
    date = models.DateTimeField(auto_now_add=True)
    ''' Extra information e.g. collected by for collection '''
    extra_information = models.TextField()

class Payment(ModelWithStatus):
    PAYMENT_PURPOSE_CHOICE = (('B', 'Bulk plan'),
        ('O', 'Order'),)

    PAYMENT_INSTRUMENT_CHOICE = (('C', 'Cash'),
        ('O', 'Electronic (Web, ATM, Transfer)'),
        ('B', 'Bank (Teller)'),)

    purpose = models.CharField(max_length=1, 
                               choices=PAYMENT_PURPOSE_CHOICE,)

    instrument = models.CharField(max_length=1, 
                               choices=PAYMENT_INSTRUMENT_CHOICE,)

    reference = models.CharField(max_length=30, blank=True, null=True,)

    date = models.DateTimeField()

    cashier = models.ForeignKey(User,)

class OrderPayment(models.Model):
    PAYMENT_TYPE_CHOICE = (('A', 'Advance'),
        ('B', 'Balance'),
        ('C', 'Complete'),)

    order = models.ForeignKey(Order,)
    payment = models.OneToOneField(Payment,)
    type = models.CharField(max_length=1, choices=PAYMENT_TYPE_CHOICE)

class BulkPlanPayment(models.Model):
    bulk_plan = models.ForeignKey(BulkPlan,)
    payment = models.OneToOneField(Payment,)
    month = models.PositiveSmallIntegerField(max_length=1, choices=MONTH_CHOICE)
