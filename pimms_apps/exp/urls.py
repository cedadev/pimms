from django.conf.urls.defaults import *

# Enabling the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
            
    #----------Experiments-------------------------------------------
    
    # exp 'home' page (experiment list page)                   
    (r'^$','pimms_apps.exp.views.exphome', {}, 'exphome'),
    
    #add new experiment page 
    (r'^expadd/$', 'pimms_apps.exp.views.expadd', {}, 'expadd'),
    
    #view experiment page 
    (r'^expview/(?P<expid>\d+)/$', 'pimms_apps.exp.views.expview', {}, 'expview'),
    
    #edit experiment page 
    (r'^expedit/(?P<expid>\d+)/$', 'pimms_apps.exp.views.expedit',{}, 'expedit'),
     
    #copy experiment page 
    (r'^expcopy/(?P<expid>\d+)/$', 'pimms_apps.exp.views.expcopy',{}, 'expcopy'),
                       
    #delete experiment page 
    (r'^expdelete/(?P<expid>\d+)/$', 'pimms_apps.exp.views.expdelete',{}, 'expdelete'),
    
    #publish experiment page 
    (r'^exppub/(?P<expid>\d+)/$', 'pimms_apps.exp.views.exppub',{}, 'exppub'),
    
    
    #----------Requirements---------------------------------------------
    
    #requirements list page
    (r'^reqlist/$', 'pimms_apps.exp.views.reqlist',{}, 'reqlist'),
    
    #add new requirement page 
    (r'^reqadd/$', 'pimms_apps.exp.views.reqadd',{}, 'reqadd'),
    
    #view requirement page 
    (r'^reqview/(?P<reqid>\d+)/$', 'pimms_apps.exp.views.reqview',{}, 'reqview'),
    
    #edit requirement page 
    (r'^reqedit/(?P<reqid>\d+)/$', 'pimms_apps.exp.views.reqedit',{}, 'reqedit'),
    
    #delete experiment page 
    (r'^reqdelete/(?P<reqid>\d+)/$', 'pimms_apps.exp.views.reqdelete',{}, 'reqdelete'),
        
    )
