from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^$', 'pimms_apps.qn.qnsetup.views.qnsetuphome', {}, 'qnsetuphome'),
    (r'^qninputs$', 'pimms_apps.qn.qnsetup.views.qninputs', {}, 'qninputs'),
    (r'^success/(?P<qnproj>\w+)/$', 'pimms_apps.qn.qnsetup.views.qnsetupsuccess', {}, 'qnsetupsuccess'),
    )