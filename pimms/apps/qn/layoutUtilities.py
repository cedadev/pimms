import string

from django.conf import settings
from django.core.urlresolvers import reverse

from pimms.apps.qn.models import *
from pimms.apps.qn.utilities import RingBuffer

logging=settings.LOG


def esgurl(modelname=None, simname=None):
    '''
    Return a url construct for cim document viewing within the ESG portal
    ''' 
    
    esgurl = 'http://www.earthsystemgrid.org/trackback/query.htm?id=esg%3amodel_' \
      +modelname+'_'+simname+'&session=true'
    
    return esgurl


def getpubs():
    '''
    Return a list of published CIM documents for instantiating a datatable 
    '''
    
    # Create a dictionary of document type mapping terms 
    cimTypes={'simulation':{'class':Simulation},
              'component':{'class':Component},
              'experiment':{'class':Experiment},
              'grid':{'class':Grid},
              'platform':{'class':Platform},
             }
    
    # generate initial queryset of all CIMObjects (not including exps for now)
    allpubs = list(CIMObject.objects.exclude(cimtype='experiment').order_by('created'))
    # only take the latest version of each document
    pubs=[]
    for pub in allpubs:
        # Check if I'm a duplicate
        duplicates = list(CIMObject.objects.filter(uri=pub.uri).order_by('documentVersion'))
        if len(duplicates)>1:
            # If so, include me if I'm the most recent
            if pub == duplicates[-1]:
                pubs.append(pub)
        else:
            pubs.append(pub)
    
    for pub in pubs:
        
        # attach extra attributes to queryset
        cimType=pub.cimtype
        
        if cimType not in cimTypes:
            raise ValueError('Unknown cim type %s' %cimType)
        try:
            cimTarget = cimTypes[cimType]
            document = cimTarget['class'].objects.filter(isDeleted=False).get(
                                                                    uri=pub.uri)
            
            # attach document centre name
            pub.centrename = document.centre
            pub.abbreviation = document.abbrev
            
            # attach a url path to esg portal view (limited to most recent 
            # version of simulations) - also get the models/exps used for 
            # simulations
            try: 
                if cimType =='simulation':
                    #get most up-to-date version
                    utdsim = (CIMObject.objects.filter(uri=pub.uri).order_by(
                                                        '-documentVersion'))[0]
                    if pub == utdsim:
                        modelname = str(document.numericalModel).lower()
                        expname = str(document.experiment).lower()
                        simname = str(document.abbrev) \
                              .replace(" ","_").lower()
                        
                        #attach esg url link
                        pub.esgurl = esgurl(modelname=modelname, 
                                            simname=simname)
                        #attach model name associaed with simualtion
                        pub.usesmodel = modelname
                        pub.forexp = expname
                    else:
                        pub.esgurl = ''
                        pub.usesmodel = '---'
                        pub.forexp = '---'
                else:
                    pub.usesmodel = '---'                    
                    pub.forexp = '---'
            except:
                pub.esgurl = ''
                pub.usesmodel = '---'
                pub.forexp = '---'
                
        except:
            pub.centrename = ''
            pub.esgurl = ''
            
    return pubs


def getsims(qn):
    '''
    Return a list of centre simulations for instantiating a datatable 
    '''
       
    # generate initial queryset of all simulations
    tablesims = Simulation.objects.filter(qn=qn).filter(isDeleted=False)
    
    for s in tablesims:
        #get individual sim edit url
        s.url = reverse('pimms.apps.qn.views.simulationEdit', args=(qn, s.id))   
        #get individual sim copy url
        s.copysimurl = reverse('pimms.apps.qn.views.simulationCopyInd', args=(qn, s.id))
        #get individual sim delete url (for non-published sims)
        if len(CIMObject.objects.filter(uri=s.uri)):
            s.delurl = None
        else:     
            s.delurl=reverse('pimms.apps.qn.views.simulationDel', args=(qn, s.id))     
    
    return tablesims


class tab:
    ''' 
    This is a simple tab class to support navigation tabs 
    '''
    
    def __init__(self,name,url,active=0, pos='left'):
        self.name=name # what is seen in the tab
        self.url=url
        self.active=active
        self.pos=pos
        #print 't[%s,%s]'%(self.name,self.url)
    def activate(self):
        self.active=1
    def deactivate(self):
        self.active=0
    def obscure(self):
        self.active=-1


class tabs(list):
    ''' 
    Build a list of tabs to be used on each page, and provide a history 
    list, via cookie, to be passed to base.html 
    '''
    
    history_length = 5
    
    def __init__(self, request, qn, page, object_id=0):
        list.__init__(self)
        self.request = request
        self.qn  = qn
        
        # we keep the last model and simulation in the session cookie
        if page == 'Model':
            request.session['Model'] = object_id
        elif page == 'Simulation':
            request.session['Simulation'] = object_id
        elif page == 'Grid':
            request.session['Grid'] = object_id
            
        # need to allow for the case when neither have yet been viewed
        if 'Simulation' not in request.session:
            request.session['Simulation'] = 0
        if 'Model' not in request.session:
            request.session['Model'] = 0
        if 'Grid' not in request.session:
            request.session['Grid'] = 0
        
        #This is the list of tabs '''
        self.tablist=[
            ('Summary', 'pimms.apps.qn.views.qnhome', (qn,), 'left'),
            ('Experiments', 'pimms.apps.qn.views.simulationList', (qn,), 'left'),
            ('Model', 'pimms.apps.qn.views.componentEdit', (qn, request.session['Model'],), 'left'),
            ('Grid', 'pimms.apps.qn.views.gridEdit', (qn, request.session['Grid'],) ,'left'),
            ('Simulation', 'pimms.apps.qn.views.simulationEdit', (qn, request.session['Simulation'],), 'left'),
            #('Files', 'pimms.apps.qn.views.list', (qn, 'file',), 'left'),
            #('References', 'pimms.apps.qn.views.list', (qn, 'reference',), 'left'),
            #('Parties', 'pimms.apps.qn.views.list', (qn, 'parties',), 'left'),
            #('Help', 'pimms.apps.qn.views.help', (qn,), 'right'),
            #('About', 'pimms.apps.qn.views.about', (qn,), 'right'),
            ]
        
        for item in self.tablist:
            self.append(self.tabify(item, page))
            
        self.history(request,page)
            
    def tabify(self,item,page):
        if item[0] not in ['Simulation','Model','Grid']:
            #it's easy:
            return tab(item[0], reverse(item[1], args=item[2]), page==item[0], item[3])
          
        else:
            if item[2][1]==0:
                return tab(item[0],'',-1, item[3])
            else: 
                try:
                    obj={'Model':Component,'Simulation':Simulation,'Grid':Grid}[item[0]].objects.get(id=item[2][1])
                except:
                    logging.info('Attempt to access deleted component, simulation or grid %s,%s'%(item[0],item[2][1]))
                    return tab(item[0],'',-1,item[3] )
                
                return tab('%s:%s'%(item[0][0:5],obj), reverse(item[1],args=item[2]), page==item[0], item[3])
            
            
    def history(self,request,page):
        #initialise as necessary.
        if 'History' not in request.session:request.session['History']=RingBuffer(self.history_length)
        #append the path and name for later use in a link ...
        request.session['History'].append((request.path,page))
     
