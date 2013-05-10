from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # translator home page
    (r'^$','pimms.apps.cv.views.cvhome', {}, 'cvhome'),
    )

