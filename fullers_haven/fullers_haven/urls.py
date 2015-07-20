from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from app.views import CustomerViewSet

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = patterns('',
    # Examples:
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
