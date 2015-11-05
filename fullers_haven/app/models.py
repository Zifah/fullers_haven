from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from dateutil import parser
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models.query_utils import Q
from app.utility import GlobalOperations

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

class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class ModelWithStatus(models.Model):
    """
    A model that has a status: active or inactive
    """
    STATUS_CHOICE = ((0, 'Inactive'),
    (1, 'Active'),)
    status = models.CharField(max_length=1, choices=STATUS_CHOICE, default=1)

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

    def _get_full_name(self):
        return "{0} {1}".format(self.user.first_name, self.user.last_name)

    def _get_email(self):
        return self.user.email

    def _get_date_registered(self):
        return self.user.date_joined

    def _get_user_type(self):
        return "Staff" if self.user.is_staff else "Customer"
    #properties
    username = property(__str__)
    full_name = property(_get_full_name)
    email = property(_get_email)
    date_registered = property(_get_date_registered)
    user_type = property(_get_user_type)

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
    type = models.CharField(max_length=1, choices=PRODUCT_TYPE_CHOICE,default='M')
    price = models.DecimalField(max_digits=8, decimal_places=2,)
    #code = models.CharField(max_length=3, blank=True, null=True)

    def _get_item_names(self):
        names = ""
        for item in self.items.all():
            names += "{0}, {1}".format(names, item.name)
        return names.strip(',')

    def _get_number_of_items(self):
        number_of_items = 0

        for item in self.items.all():
            number_of_items += item.quantity

        return number_of_items

    def __str__(self):
        return self.name

    items_string = property(_get_item_names)
    number_of_items = property(_get_number_of_items)

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
        if self.latest_activation_date == date.min:
            return date.min

        latest_activation_date = self.latest_activation_date        
        latest_expiration_date = latest_activation_date + relativedelta(months=self.number_of_months_valid)
        return latest_expiration_date

    def _get_latest_activation_date_text(self):
        if self.latest_activation_date == date.min:
            return "N/A"
        else:
            return GlobalOperations.get_date_as_text(self.latest_activation_date, False)

    _get_latest_activation_date_text.short_description = "Last activated on"

    def _get_latest_expiration_date_text(self):
        if self.latest_expiration_date == date.min:
            return "N/A"
        else:
            return GlobalOperations.get_date_as_text(self.latest_expiration_date, False)

    _get_latest_expiration_date_text.short_description = "Expires(d) on"

    
    def _is_plan_active(self):
        current_month_year = date(date.today().year, date.today().month, 1)

        #is_active = current_month_year >= activation_month_year and
        #current_month_year < expiration_month_year
        is_active = current_month_year >= self.latest_activation_date and current_month_year < self.latest_expiration_date

        return is_active

    def _get_status(self):        
        return "Active" if self.is_active else "Expired"    

    def _get_orders_processed_within_current_activation(self):
        if not self.is_active:
            return ()

        orders_processed = Order.objects.all().filter(Q(date_initiated__gte = self.latest_activation_date), 
                                                  Q(customer = self.owner),
                                                  Q(date_initiated__lt = self.latest_expiration_date), 
                                                  Q(type = 'B'),
                                                  ~Q(status = 'C'))

        return orders_processed

    def _get_no_of_items_processed(self):
    #get all of the customer's bulk orders greater than or equal to first date
    #of month of current activation period
        orders_processed = self.orders_processed_with_current_activation

        no_of_items = OrderItem.objects.filter(Q(order_product__order__in = orders_processed)).count()
        return no_of_items

    def get_processed_count_for_product(self, product_id):
        orders_processed = self.orders_processed_with_current_activation
        number_processed = OrderProduct.objects.filter(Q(order__in = orders_processed),Q(product__pk = product_id)).count()
        return number_processed

    def _get_no_of_items_left(self):
        total_available = self.number_of_items if self.is_active else 0
        return total_available - self.pieces_used

    def __str__(self):
        return "Bulk plan for {0}".format(self.owner)

    owner = models.OneToOneField(User, related_name="bulk_plan")
    price = models.DecimalField(max_digits=8, decimal_places=2,)
    number_of_items = models.PositiveSmallIntegerField(verbose_name="Total pieces")
    number_of_months_valid = models.PositiveSmallIntegerField()

    is_active = property(_is_plan_active)
    status = property(_get_status)
    name = property(__str__)
    latest_activation_date = property(_get_latest_activation_date,)
    latest_expiration_date = property(_get_latest_expiration_date,)    
    latest_activation_date_text = property(_get_latest_activation_date_text,)
    latest_expiration_date_text = property(_get_latest_expiration_date_text,)
    orders_processed_with_current_activation = property(_get_orders_processed_within_current_activation)
    pieces_used = property(_get_no_of_items_processed)
    pieces_left = property(_get_no_of_items_left)
    name = property(__str__)

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
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICE)

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

    objects = GetOrNoneManager()

    order_number = models.CharField(max_length=20, unique=True,)

    date_initiated = models.DateTimeField()

    '''date order is scheduled to be picked up'''
    date_fulfillment_scheduled = models.DateField()

    '''date when the order became ready for pickup'''
    date_fulfillment_actual = models.DateField(blank=True, null=True)

    '''date when the completed order was received by the customer'''
    date_delivered = models.DateField(blank=True, null=True)

    customer = models.ForeignKey(User, related_name='orders')

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

    status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICE, default='P')

    comments = models.TextField()

    def __str__(self):
        return "{0}'s {1} order #{2}".format(self.customer, self.type_text, self.order_number)

    def _get_type_text(self):
        return dict(self.ORDER_TYPE_CHOICE)[self.type]

    _get_type_text.short_description = 'Type'

    def _get_number_of_items(self):
        number_of_items = OrderItem.objects.filter(order_product__order = self).count()
        return number_of_items

    def _get_amount_paid(self):
        total_paid = OrderPayment.objects.filter(Q(order=self), Q(payment__status=1)).aggregate(Sum("payment__amount"))["payment__amount__sum"]
        
        if total_paid is None:
            total_paid = 0

        return total_paid

    def _get_payment_status(self):
        #options: Not paid, Partly paid, Fully paid
        payment_status = "Fully paid"

        if self.type == 'B':
            pass
        else:
            if not self.amount_paid:
                payment_status = "Not paid"
            elif self.amount_paid < self.amount_payable:
                payment_status = "Partly paid"

        return payment_status
    
    def _get_items(self):
        items = OrderItem.objects.filter(Q(order_product__order=self)).order_by("item_tag")
        return items
    
    def _get_payments(self):
        payments = OrderPayment.objects.filter(Q(order=self), Q(payment__status=1))
        return payments  

    def _get_customer_name(self):
        return self.customer.profile.full_name

    def _get_distinct_order_products(self):
        queryset = self.order_products.all()
        excludes = []
        already_seen_product_id = []
        for order_product in queryset:
            if order_product.product.id in already_seen_product_id:
                excludes.append(order_product.id)
            else:
                already_seen_product_id.append(order_product.product.id)

        queryset = queryset.exclude(pk__in=excludes)
        return queryset


    customer_name = property(_get_customer_name)
    number_of_items = property(_get_number_of_items)
    amount_paid = property(_get_amount_paid)
    payment_status = property(_get_payment_status)
    items = property(_get_items)
    payments = property(_get_payments)
    type_text = property(_get_type_text)
    order_products_distinct = property(_get_distinct_order_products)

class OrderProduct(models.Model):
    '''
    Fields: order, product, serial_number, product_name, product_price
    '''
    order = models.ForeignKey(Order, related_name='order_products')
    product = models.ForeignKey(Product,)
    serial_number = models.PositiveSmallIntegerField(default=0)
    ''' the name of the product as at the creation time of this order '''
    product_name = models.CharField(max_length=50,)
    '''each item row bears the price of the container product'''
    product_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def _get_product_count_in_order(self):
        return OrderProduct.objects.filter(Q(product = self.product), Q(order = self.order)).count()

    def _get_product_total_price_in_order(self):
        return self.product_price * self.count

    count = property(_get_product_count_in_order)
    aggregate_price = property(_get_product_total_price_in_order)

    def _get_distinct_order_items(self):
        queryset = self.order_items.all()

        excludes = []
        already_seen_items = []

        for order_item in queryset:
            if order_item.item.id in already_seen_items:
                excludes.append(order_item.id)
            else:
                already_seen_items.append(order_item.item.id)

        queryset = queryset.exclude(pk__in=excludes)
        return queryset

    order_items_distinct = property(_get_distinct_order_items)

class OrderItem(models.Model):
    '''
    Fields: order_product, item, serial_number, item_name, colour, alteration, item_tag
    '''
    order_product = models.ForeignKey(OrderProduct, related_name='order_items')
    item = models.ForeignKey(Item,)
    ''' previously wanted to call this: Product number '''
    serial_number = models.PositiveSmallIntegerField(default=0)
    ''' the name of the item as at the creation time of this order '''
    item_name = models.CharField(max_length=50,)
    colour = models.ForeignKey(Colour,)
    ''' 
    either alteration or alteration_text is filled; both cannot be filled
    at the same time
    '''
    alteration = models.ForeignKey(Alteration, blank=True, null=True)
    alteration_text = models.CharField(max_length=255, blank=True, null=True)
    
    item_tag = models.CharField(max_length=50, unique=True)

    def _get_item_count_in_product(self):
        return OrderItem.objects.filter(Q(item = self.item), Q(order_product = self.order_product)).count()

    count = property(_get_item_count_in_product)

class OrderAction(models.Model):
    '''    
    Fields: order, action, actor, date, extra_information
    Order_Action_Choice: C, F, X, D
    '''
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

    amount = models.DecimalField(max_digits=15, decimal_places=2,default=0)

    payer = models.CharField(max_length=255, blank=True, null=True)

    customer = models.ForeignKey(User, related_name='payments', blank=True, null=True)

    purpose = models.CharField(max_length=1, 
                               choices=PAYMENT_PURPOSE_CHOICE,)

    instrument = models.CharField(max_length=1, 
                               choices=PAYMENT_INSTRUMENT_CHOICE,)

    reference = models.CharField(max_length=30, blank=True, null=True,)

    date = models.DateTimeField(auto_now_add=True)

    cashier = models.ForeignKey(User,)

    def _get_instrument_text(self):
        return dict(self.PAYMENT_INSTRUMENT_CHOICE)[self.instrument]

    def _get_purpose_text(self):
        return dict(self.PAYMENT_PURPOSE_CHOICE)[self.purpose]

    instrument_text = property(_get_instrument_text)
    purpose_text = property(_get_purpose_text)

    def __str__(self):
        return "{0} naira {1} payment for {2}".format(self.amount, self.instrument_text, self.purpose_text)
    

class OrderPayment(models.Model):
    #PAYMENT_TYPE_CHOICE = (('A', 'Advance'),
    #    ('B', 'Balance'),
    #    ('C', 'Complete'),)

    order = models.ForeignKey(Order, limit_choices_to={'type': 'N'})

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="order_payment", limit_choices_to={'order_payment': None,
                                                       'bulk_plan_payment': None,
                                                       'purpose': 'O'
                                                       })

    def __str__(self):
        return "{0} naira {1} payment for {2}'s normal order #{3}".format(self.payment.amount, self.payment.instrument_text, self.order.customer.profile.full_name, self.order.order_number,)

    def _get_payment_amount(self):
        return self.payment.amount

    def _get_customer_name(self):
        return self.order.customer.profile.full_name

    def _get_order_number(self):
        return self.order.order_number

    def _get_payment_date(self):
        return self.payment.date

    amount = property(_get_payment_amount)
    customer_name = property(_get_customer_name)
    order_number = property(_get_order_number)
    payment_date = property(_get_payment_date)

class BulkPlanPayment(models.Model):
    bulk_plan = models.ForeignKey(BulkPlan,)
    payment = models.OneToOneField(Payment,related_name="bulk_plan_payment", limit_choices_to={'order_payment': None,
                                                                                               'bulk_plan_payment': None,
                                                                                               'purpose': 'B'
                                                                                               }
                                   )
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICE)

    def _get_payment_amount(self):
        return self.payment.amount

    def _get_customer_name(self):
        try:
            return self.bulk_plan.owner.profile.full_name        
        except:
            return self.bulk_plan.owner.username

    def _get_month(self):
        return dict(MONTH_CHOICE)[self.month]

    _get_month.short_description = "Month"

    def _get_payment_date(self):
        return self.payment.date

    amount = property(_get_payment_amount)
    customer_name = property(_get_customer_name)
    month_display = property(_get_month)
    payment_date = property(_get_payment_date)
