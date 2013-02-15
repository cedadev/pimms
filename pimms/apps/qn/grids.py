# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.context import RequestContext

from pimms.apps.qn.models import *
from pimms.apps.qn.forms import *
from pimms.apps.qn.yuiTree import *
from pimms.apps.qn.utilities import RemoteUser
from pimms.apps.qn.layoutUtilities import tabs


logging = settings.LOG

    
class gridHandler(object):
    
    def __init__(self, qn, grid_id=None):
        ''' 
        Instantiate a grid handler, by loading existing grid information 
        '''
        
        self.qn    = qn
        self.pkid  = grid_id
        self.Klass = 'Unknown by grid handler as yet'
        
        if grid_id is None:
            ''' This is a new grid '''
            original = Grid.objects.filter(abbrev='Grid Template').get(qn=qn)
            self.grid = original.copy(qn)
        else:
            try:
                self.grid=Grid.objects.get(id=grid_id)
                self.Klass=self.grid.__class__
            except Exception,e:
                logging.debug('Attempt to open an unknown grid %s'%grid_id)
                raise Exception,e
        
        self.url = reverse('pimms.apps.qn.views.gridEdit', args=(self.qn, self.grid.id))
       
            
    def edit(self, request):
        ''' 
        Provides a form to edit a grid, and handle the posting of a form
        containing edits for a grid, or a delete 
        '''
        
        g = self.grid
        logging.debug('Starting editing grid %s' %g.id)
                        
        # find my own urls ...
        urls = {}
        urls['form'] = self.url
        #urls['refs'] = reverse('pimms.apps.qn.views.assign', args=(self.centre_id, 'reference', 'grid', g.id, ))
        #urls=commonURLs(g.grid,urls)
        
        baseURL = reverse('pimms.apps.qn.views.gridAdd', args=(self.qn, ))
        template = '+EDID+'
        baseURL = baseURL.replace('add/', '%s/edit' %template)
        
        refs = Reference.objects.filter(grid__id = g.id)
            
        postOK = True
        if request.method == "POST":
            pform = ParamGroupForm(g, request.POST, prefix='props')
            pform.newatt = 1
            gform = GridForm(request.POST, prefix='gen', instance=g)
            if gform.is_valid():
                g = gform.save()
                g = RemoteUser(request,g)
                logging.debug('Saving grid %s details (e.g. uri %s)' %(g.id, g.uri))
            else:
                logging.debug('Unable to save characteristics for grid %s' %g.id)
                postOK = False
                logging.debug(gform.errors)
            
            ok = pform.save()
            if postOK: 
                postOK = ok  # if not postok, ok value doesn't matter
        
        # We separate the response handling so we can do some navigation in the
        # meanwhile ...
        
        navtree = gridyuiTree2(g.id, baseURL, template=template)
        
        #FIXME; we'll need to put this in the right places with instances:
    
        if request.method == 'POST':
            if postOK:
                #redirect, so repainting the page doesn't resubmit
                logging.debug('Finished handling post to %s' %g.id)
                return HttpResponseRedirect(urls['form'])
            else:
                pass
                # don't reset the forms so the user gets an error response.
        else:
            #get some forms
            gform = GridForm(instance=g, prefix='gen')
            
            pform = ParamGroupForm(g, prefix='props')
            pform.newatt = 1
                
        logging.debug('Finished handling %s to grid %s' %(request.method, g.id))
        
        return render_to_response('qn/gridMain.html',
                                 {'g': g,
                                  'gform': gform, 
                                  'pform': pform,
                                  'navtree': navtree.html,
                                  'refs': refs,
                                  'urls': urls,
                                  'tabs': tabs(request, self.qn, 'Grid', self.grid.topGrid.id),
                                  'notAjax': not request.is_ajax()},
                                   context_instance=RequestContext(request))
        
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
   