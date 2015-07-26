from django.contrib import admin
from app.models import ItemCategory, Item, Product, Alteration, Discount, Order, BulkPlan, Colour, BulkPlanActivation, BulkPlanItem, ProductItem, UserProfile
from django.contrib.auth.models import User
from app.forms import BulkPlanActivationForm
from django.db.models.query_utils import Q
from django.contrib.auth.admin import UserAdmin

class ItemCategoryAdmin(admin.ModelAdmin):
    exclude = ('status',)
    list_display = ('name', 'description',)

class ItemAdmin(admin.ModelAdmin):
    exclude = ('status',)
    list_display = ('name', 'price',)

    def save_model(self, request, obj, form, change):
        new_item = super(ItemAdmin, self).save_model(request, obj, form, change)

        #Create a new product with this item as the only item in it
        if not change:
            new_product = Product(name=obj.name, type='A', price=obj.price)
            new_product.save()
            new_product.items.create(item=obj, quantity=1)

        #update the product with the changes to the item
        else:
            twin_product = ProductItem.objects.get(Q(product__type='A'), Q(item=obj), Q(quantity=1)).product
            twin_product.name = obj.name
            twin_product.price = obj.price
            twin_product.save()

        return new_item

class ProductItemInline(admin.TabularInline):
    model = ProductItem
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    exclude = ('status', 'type',)
    inlines = [ProductItemInline,]
    list_display = ('name', 'price', 'items_string')

class AlterationAdmin(admin.ModelAdmin):
    exclude = ('status',)

class DiscountAdmin(admin.ModelAdmin):
    exclude = ('status',)
    list_display = ('name', 'percentage', 'amount')


class OrderAdmin(admin.ModelAdmin):
    #no edit
    pass

class BulkPlanItemInline(admin.TabularInline):
    model = BulkPlanItem
    extra = 1

class BulkPlanAdmin(admin.ModelAdmin):
    #custom add and edit
    list_display = ('name', 'status', 'number_of_items', 'pieces_used', 'pieces_left',)
    inlines = [BulkPlanItemInline,]

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            read_only = ('owner', 'status',)
            
            if obj.is_active:
                read_only += ('number_of_items', 'price', 'number_of_months_valid',)
            return self.readonly_fields + read_only
        return self.readonly_fields

    def render_change_form(self, request, context, obj=None, *args, **kwargs):
        admin_form = context['adminform'].form  
        filter = Q(bulk_plan=None)
        
        if obj:
            filter |= Q(id = obj.id)

        try:
            admin_form.fields['owner'].queryset = User.objects.filter(filter)
        except:
            pass
            #Oops. There was an error. Now, I have to go another round of snooping around
        return super(BulkPlanAdmin, self).render_change_form(request, context, args, kwargs)

class BulkPlanActivationAdmin(admin.ModelAdmin):
    #custom add and edit
    def render_change_form(self, request, context, *args, **kwargs):
        admin_form = context['adminform'].form  
        admin_form.fields['activated_by'].queryset = User.objects.filter(id=request.user.id)
        return super(BulkPlanActivationAdmin, self).render_change_form(request, context, args, kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            read_only = ('bulk_plan',)
            return read_only
        return self.readonly_fields


    list_display = ('name', 'date_activated', 'activated_by', 'month')
    form = BulkPlanActivationForm

class ColourAdmin(admin.ModelAdmin):
    exclude = ('status',)

class MyUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        result = super(MyUserAdmin, self).save_model(request, obj, form, change)

        if not change:
            profile = UserProfile(user=obj)
            profile.save()

        return result


admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Alteration, AlterationAdmin)
admin.site.register(Discount, DiscountAdmin)

admin.site.register(Order, OrderAdmin)
admin.site.register(BulkPlan, BulkPlanAdmin)
admin.site.register(BulkPlanActivation, BulkPlanActivationAdmin)
admin.site.register(Colour, ColourAdmin)

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
