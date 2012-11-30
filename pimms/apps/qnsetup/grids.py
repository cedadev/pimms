# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from pimms.apps.qn.models import *
from pimms.apps.qn.forms import *
from pimms.apps.qn.yuiTree import *
from pimms.apps.qn.utilities import RemoteUser
from pimms.apps.qn.layoutUtilities import tabs


logging = settings.LOG

    
class gridHandler(object):
    
    def __init__(self,centre_id,grid_id=None):
        ''' Instantiate a grid handler, by loading existing grid information '''
        
        self.centre_id=centre_id
        self.pkid=grid_id
        self.Klass='Unknown by grid handler as yet'
        
        if grid_id is None:
            ''' This is a new grid '''
            cmip5c=Centre.objects.get(abbrev='CMIP5')
            original=Grid.objects.filter(abbrev='Grid Template').get(centre=cmip5c)
            self.grid=original.copy(Centre.objects.get(id=centre_id))
        else:
            try:
                self.grid=Grid.objects.get(id=grid_id)
                self.Klass=self.grid.__class__
            except Exception,e:
                logging.debug('Attempt to open an unknown grid %s'%grid_id)
                raise Exception,e
        
        self.url=reverse('pimms.apps.qn.views.gridEdit',
                         args=(self.centre_id,self.grid.id))
       
            
    def edit(self,request):
        ''' Provides a form to edit a grid, and handle the posting of a form
        containing edits for a grid, or a delete'''
        
        c=self.grid
        logging.debug('Starting editing grid %s'%c.id)
        
        #TODO; figure out if we want to keep the idea of a 'controlled' grid component, i.e. do we want the 
        #ability to add extra grid components (doubtful) - I've removed the delete capability for now:
        
                        
        # find my own urls ...
        urls={}
        urls['form']=self.url
        urls['refs']=reverse('pimms.apps.qn.views.assign',args=(self.centre_id,'reference',
                             'grid',c.id,))
        #urls=commonURLs(c.grid,urls)
        
        baseURL=reverse('pimms.apps.qn.views.gridAdd',args=(self.centre_id,))
        template='+EDID+'
        baseURL=baseURL.replace('add/','%s/edit'%template)
        
        refs=Reference.objects.filter(grid__id=c.id)
            
        postOK=True
        if request.method=="POST":
            pform=ParamGroupForm(c,request.POST,prefix='props')
            pform.newatt=1
            cform=GridForm(request.POST,prefix='gen',instance=c)
            if cform.is_valid():
                c=cform.save()
                c=RemoteUser(request,c)
                logging.debug('Saving grid %s details (e.g. uri %s)'%(c.id,c.uri))
            else:
                logging.debug('Unable to save characteristics for grid %s'%c.id)
                postOK=False
                logging.debug(cform.errors)
            ok=pform.save()
            if postOK: postOK=ok  # if not postok, ok value doesn't matter
        
        # We separate the response handling so we can do some navigation in the
        # meanwhile ...
        
        navtree=gridyuiTree2(c.id,baseURL,template=template)
        
        #FIXME; we'll need to put this in the right places with instances:
    
        if request.method=='POST':
            if postOK:
                #redirect, so repainting the page doesn't resubmit
                logging.debug('Finished handling post to %s'%c.id)
                return HttpResponseRedirect(urls['form'])
            else:
                pass
                # don't reset the forms so the user gets an error response.
        else:
            #get some forms
            cform=GridForm(instance=c,prefix='gen')
            
            pform=ParamGroupForm(c,prefix='props')
            pform.newatt=1
                
        logging.debug('Finished handling %s to grid %s'%(request.method,c.id))
        return render_to_response('gridMain.html',
                {'c':c,'cform':cform,'pform':pform,
                'navtree':navtree.html,'refs':refs,
                'urls':urls,
                'tabs':tabs(request,self.centre_id,'Grid',self.grid.topGrid.id),
                'notAjax':not request.is_ajax()})
        
    def manageRefs(self,request):      
        ''' Handle references for a specific grid '''
        refs=Reference.objects.filter(grid__id=self.grid.id)
        allrefs=Reference.objects.all()
        available=[]
        c=self.grid
        for r in allrefs: 
            if r not in refs:available.append(r) 
        rform=ReferenceForm()
        refu=reverse('pimms.apps.qn.views.addReference',args=(self.centre_id,c.id,))
        baseURLa=reverse('pimms.apps.qn.views.assignReference',args=(1,1,))[0:-4]
        baseURLr=reverse('pimms.apps.qn.views.remReference',args=(1,1,))[0:-4]
        return render_to_response('gridRefs.html',
            {'refs':refs,'available':available,'rform':rform,'c':c,
            'refu':refu,'baseURLa':baseURLa,'baseURLr':baseURLr,
            'tabs':tabs(request,self.centre_id,'References for %s'%c),
            'notAjax':not request.is_ajax()})
        
        
    def copy(self):
        ''' Make a copy for later editing.'''
        centre=Centre.objects.get(id=self.centre_id)
        new=self.grid.copy(centre)
        new.abbrev=self.grid.abbrev+'cp'
        new.title=self.grid.title+'cp'
        new.save()
        url=reverse('pimms.apps.qn.views.gridEdit',args=(self.centre_id,new.id,))
        logging.info('Created new grid %s with id %s (copy of %s)'%(new,new.id,self.grid))
        return HttpResponseRedirect(url)
   