from django.conf.urls.defaults import *
from django.conf import settings
##from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

##from pimms_apps.qn.feeds import DocFeed

# this is not actually correct, since strictly we need hexadecimal following this pattern
##uuid='\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w'

script_path=settings.DEPLOYED_SCRIPT_PATH

urlpatterns = patterns('',
    (r'^(?P<qnname>\D+)/home$','pimms_apps.qn.views.qnhome', {}, 'qnhome'),
#    (r'^cmip5/publisheddocs/$','pimms_apps.qn.views.published_docs'),
#    # 
#    url(r'^cmip5/authz/$','pimms_apps.qn.views.authorisation',name='security'),
#    #        
#    # ajax vocabulary handler
#    url(r'^ajax/vocabs/(?P<vocabName>\D+)/$','pimms_apps.qn.views.completionHelper', 
#                                                name='ajax_value'),
#    url(r'^ajax/autocomplete/modelname/$', 'pimms_apps.qn.views.autocomplete_model', 
#                                                name='autocomplete_model'),
#    #
#    # generic document handling
#    # 
    (r'^(?P<qnname>\D+)/(?P<docType>\D+)/doc/(?P<pkid>\d+)/(?P<method>\D+)/$', 'pimms_apps.qn.views.genericDoc'),  
#    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/$'%uuid,'pimms_apps.qn.views.persistedDoc'),
#    (r'^cmip5/(?P<docType>\D+)/(?P<uri>%s)/(?P<version>\d+)/$'%uuid,'pimms_apps.qn.views.persistedDoc'),                     

    # 
    # COMPONENTS:
    #   
    (r'^(?P<qnname>\D+)/component/add/$', 'pimms_apps.qn.views.componentAdd'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/edit/$', 'pimms_apps.qn.views.componentEdit'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/addsub/$', 'pimms_apps.qn.views.componentSub'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/refs/$','pimms_apps.qn.views.componentRefs'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/coupling/$','pimms_apps.qn.views.componentCup'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/Inputs/$','pimms_apps.qn.views.componentInp'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/copy/$','pimms_apps.qn.views.componentCopy'),
    (r'^(?P<qnname>\D+)/component/(?P<component_id>\d+)/text/$','pimms_apps.qn.views.componentTxt'),

    #
    # SIMULATIONS
    #
    (r'^(?P<qnname>\D+)/simulation/list/$', 'pimms_apps.qn.views.simulationList'),  
    (r'^(?P<qnname>\D+)/simulation/add/(?P<experiment_id>\d+)/$', 'pimms_apps.qn.views.simulationAdd'),
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/edit/$', 'pimms_apps.qn.views.simulationEdit'),  
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/coupling/$', 'pimms_apps.qn.views.simulationCup'), 
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/coupling/(?P<coupling_id>\d+)/(?P<ctype>\D+)/$', 'pimms_apps.qn.views.simulationCup'),  
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/conformance/$', 'pimms_apps.qn.views.conformanceMain'),  
    (r'^(?P<qnname>\D+)/simulation/copy/$', 'pimms_apps.qn.views.simulationCopy'),
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/copyind/$', 'pimms_apps.qn.views.simulationCopyInd'),
    #(r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/resetCouplings/$', 'pimms_apps.qn.views.simulationCupReset'), 
    (r'^(?P<qnname>\D+)/simulation/(?P<simulation_id>\d+)/delete/$', 'pimms_apps.qn.views.simulationDel'),
#    # 
#    # GRIDS:
#    #   
    (r'^(?P<qnname>\D+)/grid/add/$','pimms_apps.qn.views.gridAdd'),
#    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/copy/$','pimms_apps.qn.views.gridCopy'),
    (r'^(?P<qnname>\D+)/grid/(?P<grid_id>\d+)/edit/$', 'pimms_apps.qn.views.gridEdit'),
#    (r'^cmip5/(?P<centre_id>\d+)/grid/(?P<grid_id>\d+)/refs/$','pimms_apps.qn.views.gridRefs'),             


    # 
    # PLATFORMS:
    # 
    (r'^(?P<qnname>\D+)/platform/add/$', 'pimms_apps.qn.views.platformEdit'),
    (r'^(?P<qnname>\D+)/platform/(?P<platform_id>\d+)/edit/$', 'pimms_apps.qn.views.platformEdit'),
    
    #
    # experiment/view/experiment_id
    (r'^(?P<qnname>\D+)/experiment/(?P<experiment_id>\d+)/$', 'pimms_apps.qn.views.viewExperiment'),
#    
#    # cmip5/conformance/centre_id/simulation_id/requirement_id/$
#    (r'^cmip5/conformance/(?P<cen_id>\d+)/(?P<sim_id>\d+)/(?P<req_id>\d+)/$',
#            'pimms_apps.qn.views.conformanceEdit'),  
#                     
#    # help, intro, about, vn history
#    (r'^cmip5/(?P<cen_id>\d+)/help/$',
#            'pimms_apps.qn.views.help'),
#    (r'^cmip5/(?P<cen_id>\d+)/vnhist/$',
#            'pimms_apps.qn.views.vnhist'),
#    (r'^cmip5/(?P<cen_id>\d+)/trans/$',
#            'pimms_apps.qn.views.trans'),              
#    (r'^cmip5/(?P<cen_id>\d+)/about/$',
#            'pimms_apps.qn.views.about'),     
#    (r'^cmip5/(?P<cen_id>\d+)/intro/$',
#            'pimms_apps.qn.views.intro'),                       
#    # ensembles ...
#    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/$',
#            'pimms_apps.qn.views.ensemble'),
#    (r'^cmip5/(?P<cen_id>\d+)/(?P<sim_id>\d+)/ensemble/(?P<ens_id>\d+)/$',
#            'pimms_apps.qn.views.ensemble'),                                               

                        
    #### generic simple views
    
    # DELETE
    (r'^(?P<qnname>\D+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$', 'pimms_apps.qn.views.delete'),
    (r'^(?P<qnname>\D+)/delete/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$', 'pimms_apps.qn.views.delete'),      
    
    # EDIT
    (r'^(?P<qnname>\D+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<returnType>\D+)/$', 'pimms_apps.qn.views.edit'),
    (r'^(?P<qnname>\D+)/edit/(?P<resourceType>\D+)/(?P<resource_id>\d+)/(?P<targetType>\D+)/(?P<target_id>\d+)/(?P<returnType>\D+)/$', 'pimms_apps.qn.views.edit'),
    
    # LIST
    (r'^(?P<qnname>\D+)/list/(?P<resourceType>\D+)/$', 'pimms_apps.qn.views.list'),
    (r'^cmip5/(?P<cen_id>\d+)/list/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)$', 'pimms_apps.qn.views.list'),
#    (r'^cmip5/(?P<cen_id>\d+)/filterlist/(?P<resourceType>\D+)$',
#            'pimms_apps.qn.views.filterlist'),
#    # ASSIGN            
     (r'^(?P<qnname>\D+)/assign/(?P<resourceType>\D+)/(?P<targetType>\D+)/(?P<target_id>\d+)/$', 'pimms_apps.qn.views.assign'),       
#            
#    # export files to CMIP5
#    (r'^cmip5/(?P<cen_id>\d+)/exportFiles/$','pimms_apps.qn.views.exportFiles'), 
#    (r'^cmip5/testFile/(?P<fname>.+)$','pimms_apps.qn.views.testFile'),
#        
#            # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
#    # to INSTALLED_APPS to enable admin documentation:
#    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
#        
#    # Vocabs
#    url(r'^cmip5/vocab/$','pimms_apps.qn.vocab.list',name="vocab_display"),
#    (r'^cmip5/vocab/(?P<vocabID>\d+)/$','pimms_apps.qn.vocab.show'),
#    #(r'^cmip5/vocab/(?P<docID>\d+)/(?P<valID>\d+)/$','pimms_apps.qn.vocab.list'),
#        
#    # Atom Feeds
#    (r'^feeds/(.*)/$', "django.contrib.syndication.views.feed", {
#        "feed_dict": {"cmip5": DocFeed,}
#        }
#    ),
#
#    # Admin
#    (r'', include('pimms_apps.qn.admin.urls')),
#    #(r'^admin/protoq/component/copy/$', 'pimms_apps.qn.admin.admin_views.modelcopy'),
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
#        urlpatterns+=patterns('',(r'^cmip5/(?P<centre_id>\d+)/%s/(?P<%s_id>\d+)/%s/$'%(doc,doc,key),'pimms_apps.qn.views.doc'))
                    
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
urlpatterns=patterns('',(r'^%s'%script_path,include(urlpatterns)))
