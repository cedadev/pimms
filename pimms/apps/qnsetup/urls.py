# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
##from django.conf import settings
##from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

##from pimms.apps.qn.feeds import DocFeed

# this is not actually correct, since strictly we need hexadecimal following this pattern
##uuid='\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w'

##script_path=settings.DEPLOYED_SCRIPT_PATH

urlpatterns = patterns('',
    # Example:
    # (r'^cmip5q/', include('cmip5q.foo.urls')),
    (r'^$','pimms.apps.qn.views.centres', {}, 'qnhome'),
#    (r'^$','pimms.apps.qn.views.centres'),
#    (r'^cmip5/$','pimms.apps.qn.views.centres'),
#    (r'^cmip5/centres/$','pimms.apps.qn.views.centres'),
#    (r'^cmip5/(?P<centre_id>\d+)/$','pimms.apps.qn.views.centre'),
#    (r'^cmip5/publisheddocs/$','pimms.apps.qn.views.published_docs'),
#    # 
#    url(r'^cmip5/authz/$','pimms.apps.qn.views.authorisation',name='security'),
#    #        
#    # ajax vocabulary handler
#    url(r'^ajax/vocabs/(?P<vocabName>\D+)/$','pimms.apps.qn.views.completionHelper', 
#                                                name='ajax_value'),
#    url(r'^ajax/autocomplete/modelname/$', 'pimms.apps.qn.views.autocomplete_model', 
#                                                name='autocomplete_model'),
#    #
#    # generic document handling
#    # 
#    (r'^cmip5/(?P<cid>\d+)/(?P<docType>\D+)/doc/(?P<pkid>\d+)/(?P<method>\D+)/$','pimms.apps.qn.views.genericDoc'),  
#    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/$'%uuid,'pimms.apps.qn.views.persistedDoc'),
#    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/(?P<version>\d+)/$'%uuid,'pimms.apps.qn.views.persistedDoc'),                     
#    # 
#    # COMPONENTS:
#    #   
#    (r'^cmip5/(?P<centre_id>\d+)/component/add/$','pimms.apps.qn.views.componentAdd'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/edit/$','pimms.apps.qn.views.componentEdit'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/addsub/$','pimms.apps.qn.views.componentSub'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/refs/$','pimms.apps.qn.views.componentRefs'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/coupling/$','pimms.apps.qn.views.componentCup'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/Inputs/$','pimms.apps.qn.views.componentInp'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/copy/$','pimms.apps.qn.views.componentCopy'),
#    (r'^cmip5/(?P<centre_id>\d+)/component/(?P<component_id>\d+)/text/$','pimms.apps.qn.views.componentTxt'),
#    #
#    # SIMULATIONS
#    #
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/list/$',
#                'pimms.apps.qn.views.simulationList'),  
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/add/(?P<experiment_id>\d+)/$',
#                'pimms.apps.qn.views.simulationAdd'),
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/edit/$',
#                'pimms.apps.qn.views.simulationEdit'),  
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/$',
#                'pimms.apps.qn.views.simulationCup'), 
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/coupling/(?P<coupling_id>\d+)/(?P<ctype>\D+)/$',
#                'pimms.apps.qn.views.simulationCup'),  
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/conformance/$',
#                'pimms.apps.qn.views.conformanceMain'),  
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/copy/$',
#                'pimms.apps.qn.views.simulationCopy'),
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/copyind/$',
#                'pimms.apps.qn.views.simulationCopyInd'),
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/resetCouplings/$',
#                'pimms.apps.qn.views.simulationCupReset'), 
#    (r'^cmip5/(?P<centre_id>\d+)/simulation/(?P<simulation_id>\d+)/delete/$',
#                'pimms.apps.qn.views.simulationDel'),
#    # 
#    # GRIDS:
#    #   
#    (r'^cmip5/(?P<centre_id>\d+)/grid/add/$','pimms.apps.qn.views.gridAdd'),
#    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/copy/$','pimms.apps.qn.views.gridCopy'),
#    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/edit/$','pimms.apps.qn.views.gridEdit'),
#    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/refs/$','pimms.apps.qn.views.gridRefs'),             
#    #           
#    # platforms/add/centre_id
#    # platforms/edit/platform_id
#    #
#    (r'^cmip5/(?P<centre_id>\d+)/platform/add/$',
#            'pimms.apps.qn.views.platformEdit'),
#    (r'^cmip5/(?P<centre_id>\d+)/platform/(?P<platform_id>\d+)/edit/$',
#            'pimms.apps.qn.views.platformEdit'),
#    #
#    # experiment/view/experiment_id
#    (r'^cmip5/(?P<cen_id>\d+)/experiment/(?P<experiment_id>\d+)/$',
#            'pimms.apps.qn.views.viewExperiment'),
#    
#    # cmip5/conformance/centre_id/simulation_id/requirement_id/$
#    (r'^cmip5/conformance/(?P<cen_id>\d+)/(?P<sim_id>\d+)/(?P<req_id>\d+)/$',
#            'pimms.apps.qn.views.conformanceEdit'),  
#                     
#    # help, intro, about, vn history
#    (r'^cmip5/(?P<cen_id>\d+)/help/$',
#            'pimms.apps.qn.views.help'),
#    (r'^cmip5/(?P<cen_id>\d+)/vnhist/$',
#            'pimms.apps.qn.views.vnhist'),
#    (r'^cmip5/(?P<cen_id>\d+)/trans/$',
#            'pimms.apps.qn.views.trans'),              
#    (r'^cmip5/(?P<cen_id>\d+)/about/$',
#            'pimms.apps.qn.views.about'),     
#    (r'^cmip5/(?P<cen_id>\d+)/intro/$',
#            'pimms.apps.qn.views.intro'),                       
#    # ensembles ...
#    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/$',
#            'pimms.apps.qn.views.ensemble'),
#    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/(?P<ens_id>\d+)/$',
#            'pimms.apps.qn.views.ensemble'),                                               
#                          
#    #### generic simple views
#    # DELETE
#    (r'^cmip5/(?P<cen_id>\d+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$',
#            'pimms.apps.qn.views.delete'),
#    (r'^cmip5/(?P<cen_id>\d+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$',
#            'pimms.apps.qn.views.delete'),      
#    # EDIT
#    # cmip5q/centre_id/edit/resourceType/resourceID/returnType  (resourceID=0, blank form)
#    (r'^cmip5/(?P<cen_id>\d+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$',
#            'pimms.apps.qn.views.edit'),
#    # cmip5q/centre_id/edit/resourceType/resourceID/targetType/targetID/returnType  
#        #(resourceID=0, blank form)
#    (r'^cmip5/(?P<cen_id>\d+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$',
#            'pimms.apps.qn.views.edit'),
#    # LIST
#    (r'^cmip5/(?P<cen_id>\d+)/list/(?P<resourceType>\D+)/$',
#            'pimms.apps.qn.views.list'),
#    (r'^cmip5/(?P<cen_id>\d+)/list/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)$',
#            'pimms.apps.qn.views.list'),
#    (r'^cmip5/(?P<cen_id>\d+)/filterlist/(?P<resourceType>\D+)$',
#            'pimms.apps.qn.views.filterlist'),
#    # ASSIGN            
#    (r'^cmip5/(?P<cen_id>\d+)/assign/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)/$',
#            'pimms.apps.qn.views.assign'),       
#            
#    # export files to CMIP5
#    (r'^cmip5/(?P<cen_id>\d+)/exportFiles/$','pimms.apps.qn.views.exportFiles'), 
#    (r'^cmip5/testFile/(?P<fname>.+)$','pimms.apps.qn.views.testFile'),
#        
#            # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
#    # to INSTALLED_APPS to enable admin documentation:
#    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
#        
#    # Vocabs
#    url(r'^cmip5/vocab/$','pimms.apps.qn.vocab.list',name="vocab_display"),
#    (r'^cmip5/vocab/(?P<vocabID>\d+)/$','pimms.apps.qn.vocab.show'),
#    #(r'^cmip5/vocab/(?P<docID>\d+)/(?P<valID>\d+)/$','pimms.apps.qn.vocab.list'),
#        
#    # Atom Feeds
#    (r'^feeds/(.*)/$', "django.contrib.syndication.views.feed", {
#        "feed_dict": {"cmip5": DocFeed,}
#        }
#    ),
#
#    # Admin
#    (r'', include('pimms.apps.qn.admin.urls')),
#    #(r'^admin/protoq/component/copy/$', 'pimms.apps.qn.admin.admin_views.modelcopy'),
#    (r'^cmip5/admin/', include(admin.site.urls)),
#
#    #---------------------------------
#    # Metadata explorer url includes
#
#    # metadata explorer included
#    (r'^cmip5/explorer/', include('cmip5q.explorer.urls')),
#
#    # API included
#    (r'^cmip5/qnstats/', include('cmip5q.qnstats.urls')),
)


# now add the common document url methods
#for doc in ['experiment','platform','component','simulation']:
#    for key in ['validate','view','xml','html','export']:
#        urlpatterns+=patterns('',(r'^cmip5/(?P<centre_id>\d+)/%s/(?P<%s_id>\d+)/%s/$'%(doc,doc,key),'pimms.apps.qn.views.doc'))
                    
#if True:  # HACK HACK HACK POOR PERFORMANCE AND SECURITY.
#    urlpatterns += patterns('',
#        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.STATIC_DOC_ROOT,'show_indexes': True}),
#    )
#    
## To direct web crawlers to bypass potentially redundant links
#urlpatterns += patterns('',
#    (r'^robots\.txt$', direct_to_template,
#     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
#)
#
#
## finally if necessary, throw it down a level
#
#urlpatterns=patterns('',(r'^%s'%script_path,include(urlpatterns)))