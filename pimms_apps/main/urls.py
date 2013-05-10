from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # home and about pages
    (r'^$','pimms.apps.main.views.home', {}, 'home'),
    (r'^about/$','pimms.apps.main.views.about', {}, 'about'),
    )

