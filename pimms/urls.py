from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                           
    # admin:
    url(r'^admin/', include(admin.site.urls)),
        
    # for user registration/login/logout
    (r'^register/$', 'pimms.apps.person.views.UserRegistration', {}, 'register'),
    (r'^login/$', 'pimms.apps.person.views.LoginRequest', {}, 'login'),
    (r'^logout/$', 'pimms.apps.person.views.LogoutRequest', {}, 'logout'),
    
    # including app level urls.py's
    (r'', include('pimms.apps.main.urls')),
    (r'', include('pimms.apps.person.urls')),
    (r'^exp/', include('pimms.apps.exp.urls')),
    (r'^cv/', include('pimms.apps.cv.urls')),
    (r'^qnsetup/', include('pimms.apps.qn.qnsetup.urls')),
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
