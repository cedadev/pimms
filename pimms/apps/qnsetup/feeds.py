import os

from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse

from atom import Feed, AtomFeed

from pimms.apps.qn.models import *
from pimms.apps.qn.XMLutilities import etTxt


logging=settings.LOG


class TestDocs(object):
    ''' 
        Dummy queryset for test documents
    '''
    
    @staticmethod
    def getdocs(testdir):
        myfiles=[]
        for f in os.listdir(testdir):
            if f.endswith('.xml'): myfiles.append(TestDocumentSet(testdir,f))
        return TestDocs(myfiles)
    
    def __init__(self,myfiles):
        self.myfiles=myfiles
    
    def order_by(self,arg):
        #Just return the list, which probably has only one entry
        return self.myfiles


class TestDocumentSet(object):
    ''' 
        This class provides pseudo CIMObjects from files on disk 
    '''
    
    class DummyAuthor(object):
        def __init__(self):
            self.name='Test Author: Gerry Devine'
            self.email='g.m.devine@met.reading.ac.uk'
            
    def __init__(self, d, f):
        ff = os.path.join(d, f)
        ef = ET.parse(ff)
        cimns = 'http://www.purl.org/org/esmetadata/cim/1.5/schemas'
        cimdoclist = ['{%s}modelComponent' %cimns, 
                      '{%s}platform' %cimns] 
        
        if ef.getroot().find('{%s}simulationRun' %cimns) is not None:
            e=ef.getroot().find('{%s}simulationRun' %cimns)
        else:
            for cimdoc in cimdoclist:
                if ef.getroot().tag == cimdoc is not None:
                    e=ef.getroot()
            
        #--------------
        getter=etTxt(e)
        
        #basic document stuff for feed
        doc={'description':'description', 
             'shortName':'abbrev',
             'longName':'title', 
             'documentCreationDate':'created', 
             'updated':'updated', 
             'documentID':'uri'}
        
        for key in doc.keys():
            self.__setattr__(doc[key], getter.get(e, key))
        self.fname = f
        self.cimtype = 'DocumentSet'
        self.author = self.DummyAuthor()
        self.created = datetime.now()
        self.updated = datetime.now()

    def get_absolute_url(self):
        return reverse('pimms.apps.qn.views.testFile', args=(self.fname, ))
    

#class AtomEntryCustomFeed(Feed):
#    """Custom Atom feed generator.
#    This class will form the structure of the custom RSS feed.
#    It's used to add a new tag element to each of the 'item's.
#    """
#    def get_feed(self, extra_params=None):
#        
#        if extra_params:
#            try:
#                obj = self.get_object(extra_params.split('/'))
#            except (AttributeError, LookupError):
#                raise LookupError('Feed does not exist')
#        else:
#            obj = None
#        
#        feed = AtomFeed(
#            atom_id = self.__get_dynamic_attr('feed_id', obj),
#            title = self.__get_dynamic_attr('feed_title', obj),
#            updated = self.__get_dynamic_attr('feed_updated', obj),
#            icon = self.__get_dynamic_attr('feed_icon', obj),
#            logo = self.__get_dynamic_attr('feed_logo', obj),
#            rights = self.__get_dynamic_attr('feed_rights', obj),
#            subtitle = self.__get_dynamic_attr('feed_subtitle', obj),
#            authors = self.__get_dynamic_attr('feed_authors', obj, default=[]),
#            categories = self.__get_dynamic_attr('feed_categories', obj, default=[]),
#            contributors = self.__get_dynamic_attr('feed_contributors', obj, default=[]),
#            links = self.__get_dynamic_attr('feed_links', obj, default=[]),
#            extra_attrs = self.__get_dynamic_attr('feed_extra_attrs', obj),
#            hide_generator = self.__get_dynamic_attr('hide_generator', obj, default=False)
#        )
#        
#        items = self.__get_dynamic_attr('items', obj)
#        if items is None:
#            raise LookupError('Feed has no items field')
#        
#        for item in items:
#            feed.add_item(
#                atom_id = self.__get_dynamic_attr('item_id', item), 
#                title = self.__get_dynamic_attr('item_title', item),
#                updated = self.__get_dynamic_attr('item_updated', item),
#                content = self.__get_dynamic_attr('item_content', item),
#                published = self.__get_dynamic_attr('item_published', item),
#                rights = self.__get_dynamic_attr('item_rights', item),
#                source = self.__get_dynamic_attr('item_source', item),
#                summary = self.__get_dynamic_attr('item_summary', item),
#                authors = self.__get_dynamic_attr('item_authors', item, default=[]),
#                categories = self.__get_dynamic_attr('item_categories', item, default=[]),
#                contributors = self.__get_dynamic_attr('item_contributors', item, default=[]),
#                links = self.__get_dynamic_attr('item_links', item, default=[]),
#                extra_attrs = self.__get_dynamic_attr('item_extra_attrs', None, default={}),
#            )
#        
#        if self.VALIDATE:
#            feed.validate()
#        return feed
#    
#    
#    def add_item_elements(self, handler, item):
#    # Invoke this same method of the super-class to add the standard elements
#    # to the 'item's.
#        super(AtomEntryCustomFeed, self).add_item_elements(handler, item)
#
#    # Add a new custom element named 'content' to each of the tag 'item'.
#        handler.addQuickElement(u"content", item['content'])    
    

    
    
class DocFeed(Feed):
    ''' 
       This is the atom feed for xml documents available from the questionnaire
       See http://code.google.com/p/django-atompub/wiki/UserGuide
    '''
    
    #feed_type = Atom1Feed

    
    feeds = {
             'platform': CIMObject.objects.filter(cimtype = 'platform'),
             'simulation': CIMObject.objects.filter(cimtype = 'simulation'),
             'component': CIMObject.objects.filter(cimtype = 'component'),
             'experiment': CIMObject.objects.filter(cimtype = 'experiment'),
             'files': CIMObject.objects.filter(cimtype = 'dataContainer'),
             'all': CIMObject.objects.all(),
             'test': TestDocs.getdocs(settings.TESTDIR)
             }
    
    DocTypes = {
                'simulation':{'class':Simulation,'attname':'simulation'},
                'component':{'class':Component,'attname':'component'},
                'experiment':{'class':Experiment,'attname':'experiment'},
                'grid':{'class':Grid,'attname':'grid'},
                'platform':{'class':Platform,'attname':'platform'},
                }
    
    
    #Taken from atom.py
    def __get_dynamic_attr(self, attname, obj, default=None):
        try:
            attr = getattr(self, attname)
        except AttributeError:
            return default
        if callable(attr):
            # Check func_code.co_argcount rather than try/excepting the
            # function and catching the TypeError, because something inside
            # the function may raise the TypeError. This technique is more
            # accurate.
            if hasattr(attr, 'func_code'):
                argcount = attr.func_code.co_argcount
            else:
                argcount = attr.__call__.func_code.co_argcount
            if argcount == 2: # one argument is 'self'
                return attr(obj)
            else:
                return attr()
        return attr
    
    def get_feed(self, extra_params=None):
        
        if extra_params:
            try:
                obj = self.get_object(extra_params.split('/'))
            except (AttributeError, LookupError):
                raise LookupError('Feed does not exist')
        else:
            obj = None
        
        feed = AtomFeed(
            atom_id = self.__get_dynamic_attr('feed_id', obj),
            title = self.__get_dynamic_attr('feed_title', obj),
            updated = self.__get_dynamic_attr('feed_updated', obj),
            icon = self.__get_dynamic_attr('feed_icon', obj),
            logo = self.__get_dynamic_attr('feed_logo', obj),
            rights = self.__get_dynamic_attr('feed_rights', obj),
            subtitle = self.__get_dynamic_attr('feed_subtitle', obj),
            authors = self.__get_dynamic_attr('feed_authors', obj, default=[]),
            categories = self.__get_dynamic_attr('feed_categories', obj, default=[]),
            contributors = self.__get_dynamic_attr('feed_contributors', obj, default=[]),
            links = self.__get_dynamic_attr('feed_links', obj, default=[]),
            extra_attrs = self.__get_dynamic_attr('feed_extra_attrs', obj),
            hide_generator = self.__get_dynamic_attr('hide_generator', obj, default=False)
        )
        
        items = self.__get_dynamic_attr('items', obj)
        if items is None:
            raise LookupError('Feed has no items field')
        
        for item in items:
            feed.add_item(
                atom_id = self.__get_dynamic_attr('item_id', item), 
                title = self.__get_dynamic_attr('item_title', item),
                updated = self.__get_dynamic_attr('item_updated', item),
                content = self.__get_dynamic_attr('item_content', item),
                published = self.__get_dynamic_attr('item_published', item),
                rights = self.__get_dynamic_attr('item_rights', item),
                source = self.__get_dynamic_attr('item_source', item),
                summary = self.__get_dynamic_attr('item_summary', item),
                authors = self.__get_dynamic_attr('item_authors', item, default=[]),
                categories = self.__get_dynamic_attr('item_categories', item, default=[]),
                contributors = self.__get_dynamic_attr('item_contributors', item, default=[]),
                links = self.__get_dynamic_attr('item_links', item, default=[]),
                extra_attrs = self.__get_dynamic_attr('item_extra_attrs', item, default={}),
            )
        
        if self.VALIDATE:
            feed.validate()
        return feed
    
    def _mydomain(self):
        # the request object has been passed to the constructor for the Feed 
        # base class,so we have access to the protocol, port, etc
        current_site = RequestSite(self.request)
        return 'http://%s' %current_site.domain
    
    def _myurl(self, model):
        return self._mydomain() + reverse('django.contrib.syndication.views.feed', 
                                          args=('cmip5/%s'%model,))
    
    def get_object(self, params):
        ''' Used for parameterised feeds '''
        assert params[0] in self.feeds,'Unknown feed request'
        return params[0]
    
    def feed_id (self, model):
        return self._myurl(model)
    
    def feed_title(self, model):
        return 'CMIP5 %s metadata'%model
    
    def feed_subtitle(self,model):
        return 'Metafor questionnaire - completed %s documents'%model
    
    def feed_authors(self,model):
        return [{'name':'The metafor team'}]
    
    def feed_links(self,model):
        u=self._myurl(model)
        return [{"rel": "self", "href": "%s"%u}]
    
    def feed_extra_attrs(self,model):
        # additional namespace attribute added for additional entry attributes
        return {'xml:base':self._mydomain(), 'xmlns:cmip5qn': 
                'http://www.purl.org/org/esmetadata/cmip5/qn'}
    
    def items(self,model):
        return self.feeds[model].order_by('-updated')
    
    def item_id(self,item):
        return 'urn:uuid:%s'%item.uri
    
    def item_title(self,item):
        if hasattr(item, "documentVersion"):
            return '%s - Version %s' %(item.title, item.documentVersion)
        else:
            return item.title            
    
    def item_authors(self,item):
        if item.author is not None:
            return [{'name': item.author.name,'email':item.author.email}]
        else: return []
    
    def item_updated(self,item):
        return item.updated
    
    def item_published(self,item):
        return item.created
    
    def item_links(self,item):
        return [{'href':self._mydomain() + item.get_absolute_url()}]
            
    def item_summary(self,item):
        if item.description:
            return item.description
        else:
            return '%s:%s'%(item.cimtype,item.title)
    
    def item_content(self,item):
        ''' Return out of line link to the content'''
        return {"type": "application/xml", "src":item.get_absolute_url()},""
    
    def item_extra_attrs(self, item):
        '''
        Add extra attributes to each entry to tag centre name and qndrs 
        string
        '''
        
        if item.cimtype is not None:
            try:
                target=self.DocTypes[item.cimtype]
                targetdoc = target['class'].objects.filter(uri=item.uri).get(
                                        documentVersion=item.documentVersion)
                
                # get centre name
                try:
                    centrename =  str(targetdoc.centre)
                except:
                    centrename=''
                    
                # If simulation, also return the qnDRS attribute 
                if target['attname'] == 'simulation':
                    assert len(targetdoc.drsOutput.all())==1, "One and only one DRS string expected"
                    assert targetdoc.drsOutput.all()[0], "Expecting a value for the DRS string"
                    try:
                        drsstring=str(targetdoc.drsOutput.all()[0])
                    except:
                        drsstring=''  
                    'return centre name and drs string'
                    return {'cmip5qn:centre': centrename, 
                            'cmip5qn:qnDRS':drsstring}
                else:
                    # else return only the centre name
                    return {'cmip5qn:centre': centrename}
            except:
                return{}
        else:
            return {}    
  
    