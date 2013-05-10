from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/qn/component/copy/$', 'pimms_apps.qn.admin.admin_views.modelcopy'),
)
