from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # translator home page
    (r'^$','pimms.apps.qnsetup.views.qnsetuphome', {}, 'qnsetuphome'),
    (r'^qninputs$','pimms.apps.qnsetup.views.qninputs', {}, 'qninputs'),
    (r'^success$','pimms.apps.qnsetup.views.qnsetupsuccess', {}, 'qnsetupsuccess'),
    #(r'^cvload/$', 'pimms.apps.qnsetup.views.multiple_uploader', {}, 'cvload'),
    )

