from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^$', 'pimms.apps.qn.qnsetup.views.qnsetuphome', {}, 'qnsetuphome'),
    (r'^qninputs$', 'pimms.apps.qn.qnsetup.views.qninputs', {}, 'qninputs'),
    (r'^success/(?P<qnproj>\w+)/$', 'pimms.apps.qn.qnsetup.views.qnsetupsuccess', {}, 'qnsetupsuccess'),
    )