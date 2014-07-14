from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                           
    # admin:
    url(r'^admin/', include(admin.site.urls)),
        
    # for user registration/login/logout
    (r'^register/$', 'pimms_apps.person.views.UserRegistration', {}, 'register'),
    (r'^login/$', 'pimms_apps.person.views.LoginRequest', {}, 'login'),
    (r'^logout/$', 'pimms_apps.person.views.LogoutRequest', {}, 'logout'),
    
    # including app level urls.py's
    (r'', include('pimms_apps.main.urls')),
    (r'', include('pimms_apps.person.urls')),
    (r'^exp/', include('pimms_apps.exp.urls')),
    (r'^cv/', include('pimms_apps.cv.urls')),
    (r'^qn/', include('pimms_apps.qn.urls')),
    (r'^qnsetup/', include('pimms_apps.qn.qnsetup.urls')),
    (r'^bkm/', include('pimms_apps.bkm.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
    (r'^static/(?P<path>.*)$', 
        'serve', {
        'document_root': settings.STATIC_ROOT,
        'show_indexes': True }),
    (r'^media/(?P<path>.*)$', 
        'serve', {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': True }),
    )
