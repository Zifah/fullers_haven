from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from app.views import CustomerViewSet, ProductView, ColourViewSet, AlterationViewSet, OrderView, OrderInvoiceView, OrderTagsView
from django.views.generic.base import RedirectView
import debug_toolbar

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'colours', ColourViewSet)
router.register(r'alterations', AlterationViewSet)

urlpatterns = patterns('',
    # Examples:
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/products/$', ProductView.as_view(), name='products'),
    url(r'^api/v1/orders/$', OrderView.as_view(), name='orders'),
    url(r'^api/v1/orders/(?P<pk>\d+)/$', OrderView.as_view(), name='get_order'),
    url(r'^admin/app/order/(?P<pk>\d+)/receipt/$', OrderInvoiceView.as_view(), name='order_invoice'),
    url(r'^admin/app/order/(?P<pk>\d+)/tags/$', OrderTagsView.as_view(), name='order_tags'),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^$', RedirectView.as_view(url='admin', permanent=False), name='index'),
)

admin.site.site_title = 'Fullers Haven admin'
admin.site.site_header = 'Fullers Haven'