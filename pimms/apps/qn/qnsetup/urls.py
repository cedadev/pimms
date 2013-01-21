from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # translator home page
    (r'^$','pimms.apps.qn.qnsetup.views.qnsetuphome', {}, 'qnsetuphome'),
    (r'^qninputs$','pimms.apps.qn.qnsetup.views.qninputs', {}, 'qninputs'),
    (r'^success$','pimms.apps.qn.qnsetup.views.qnsetupsuccess', {}, 'qnsetupsuccess'),
    )

