from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from app.views import CustomerViewSet, ProductsView
from django.views.generic.base import RedirectView

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = patterns('',
    # Examples:
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/products/$', ProductsView.as_view(), name='products'),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^$', RedirectView.as_view(url='admin', permanent=False), name='index'),
)

admin.site.site_title = 'Fullers Haven admin'
admin.site.site_header = 'Fullers Haven'