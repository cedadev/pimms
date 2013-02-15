from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden,HttpResponseBadRequest
from django.conf import settings
from django.template.context import RequestContext

from pimms.apps.qn.models import *
from pimms.apps.qn.forms import *
from pimms.apps.qn.layoutUtilities import tabs
from pimms.apps.qn.utilities import sublist, render_badrequest


logging=settings.LOG


class BaseViewHandler:
    ''' This is a base class to be used by the editors and listers
            '''
    def __init__(self, qn, resource, target):
        ''' The base view handler is initialised with stuff that is known to the url mapping
        and exploits some knowledge of the specific resources. We shouldn't know anything
        about the specific resources in this class '''
                 
        self.qn = qn
        self.resource=resource
        self.target=target
        
        self.editHTML='qn/baseview_edit.html'#'%s_edit.html'%self.resource['type']
        self.listHTML='qn/baseview_list.html'#'%s_list.html'%self.resource['type']
        self.selectHTML='qn/baseviewAssign.html'
        
    def objects(self):
        ''' We use the subclass method '''
        return 'Not implemented'
    
    def constraints(self):
        ''' We use the subclass method'''
        return 'Not Implemented'
    
    def _constructForm(self, method, *args, **kwargs):
        ''' Handle form construction '''
        if method == 'POST':
            return self.resource['form'](self.qn, *args, **kwargs)
        elif method == 'GET':
            # FIXME we'll need to do the specialisation based on the 
            # target information ... postpone this again for now.
            form = self.resource['form'](qn=self.qn, *args, **kwargs)
            constraints = self.constraints()
            if constraints is not None: 
                form.specialise(constraints)
            
            return form
        else:
            raise ValueError('Form construction only supports GET and POST')
                 
    def list(self, request):
        ''' 
        Show a list of the basic entities, either all of them, or those
        associated with a specific instance of a specific class 
        '''
        
        objects = self.objects()
        
        #construct a set of options for filtering to a specific class (if appropriate)
        ftype = self.resource['filter']
        
        if ftype:
            url = reverse('pimms.apps.qn.views.filterlist', args=(self.qn, self.resource['type'],))
            ops = ftype.objects.all()
            
            try: # if we can filter on centres, we do ...
                ops.filter(qn__id=self.qn)
            except AttributeError: 
                pass
              
            filterops={'m':'Filter by %s'%ftype._meta.module_name,
                       'ops' : ops,
                       'url' : url,
                       'klass' : ftype._meta.module_name}
        else: 
            filterops=None
        
        # construct an export button
        if self.resource['type'] == 'file':
            exportFiles = reverse('pimms.apps.qn.views.exportFiles', args=(self.qn, ))
        else: 
            exportFiles = None
        
        if self.target:
            # in the case of a list, the target is used to go back ...

            # get a URL for a blank form
            formURL = reverse('pimms.apps.qn.views.edit',
                            args=(self.qn, self.resource['type'], 0, self.target['type'], self.target['instance'].id, 'list',))
            for o in objects:
                # monkey patch an edit URL into the object allowing for the target,
                # saying come back here (to the list). Unfortunately doing that
                # means we lose the incoming reference.
                args = (self.qn, self.resource['type'], o.id, self.target['type'], self.target['instance'].id, 'list',)
                o.editURL = reverse('pimms.apps.qn.views.edit', args=args)
                o.delURL = reverse('pimms.apps.qn.views.delete', args=args)
                #o.delURL=reverse('pimms.apps.qn.views.delete',
                #            args=(self.cid,self.resource['type'],o.id,self.currentURL)
                # Need to be able to make sure this isn't an html get from an <a> otherwise
                # do it as  form with a method of delete.
        else:
            # get a URL for a blank form
            formURL = reverse('pimms.apps.qn.views.edit', args=(self.qn, self.resource['type'], 0, 'list', ))
            
            for o in objects:
                # monkey patch an edit URL into the object, saying come back here (list)
                args = (self.qn, self.resource['type'], o.id, 'list', )
                o.editURL = reverse('pimms.apps.qn.views.edit', args=args)
                if o.qn == self.qn:
                    o.delURL = reverse('pimms.apps.qn.views.delete', args=args)
                else:
                    o.delURL = None
        # we pass a form and formURL for a new instance to be created.
        # we're doing all this because we think we have too many entities to use a formset
       
        return render_to_response(self.listHTML,{
                                                'objects'     : sublist(objects, 3),
                                                'tabs'        : tabs(request, self.qn, self.resource['tab']),
                                                'form'        : self._constructForm('GET'),
                                                'editURL'     : formURL,
                                                'instance'    : self.resource,
                                                'snippet_template': 'qn/%s_snippet.html' %self.resource['type'],
                                                'target'      : self.target,
                                                'exportFiles' : exportFiles,
                                                'filter'      : filterops},
                                                context_instance=RequestContext(request))
                
    def filterlist(self, request):
        ''' 
        construct a filter based on a posted form and redirect to a targetted list
        '''
        if request.method == 'POST':
            logging.debug('Trying to filter on %s' %request.POST)
            url = reverse('pimms.apps.qn.views.list', args=(self.qn, self.resource['type'], request.POST['klass'], request.POST['id'], ))
            return HttpResponseRedirect(url)
        else:
            return render_badrequest('error.html', {'message':'Error, No GET to filterlist'})
                
    def edit(self, request, returnType):
        ''' 
        We normally see this method called as a GET when it's hyperlinked
        from a list or assign page, so we want to go back there in those cases.
        If it's a POST, then we handle it, and go back to the correct place,
        unless there is a problem. 
        '''
            
        # The basic sequence when we receive an edit form as a post, is that 
        # if it's valid, return to where we came from. If it's not, we should show
        # a form, complete with errors, with a submission URL which gets the user
        # back to the right place.  A GET should set that process up.
        if self.target:
            okURL = reverse('pimms.apps.qn.views.%s' %returnType,
               args = (self.qn, self.resource['type'], self.target['type'], self.target['instance'].id, ))
        else:
            okURL = reverse('pimms.apps.qn.views.%s' %returnType, args=(self.qn, self.resource['type'], ))
        
        # Note that if the resource instance id is zero, this is a new one.
        instance=None
        
        if self.resource['id'] <> '0':
            instance = self.resource['class'].objects.get(id=self.resource['id'])
            
             
        # Now construct a useful submission URL
        args = [self.qn, self.resource['type'], self.resource['id']]
        
        if self.target:
            args += [self.target['type'],self.target['instance'].id]
        
        if returnType: 
            args.append(returnType)
                    
        if request.method=='POST':
            logging.debug('Handling post with %s, %s ' %(self.resource, request.POST))
            if instance:
                if instance.qn != self.qn:
                    logging.info('Attempt to edit resource not owned')
                    return HttpResponseForbidden(render_to_string('error.html',
                        {'message':"Attempt to edit a resource you don't own",
                        'url':okURL}))
            
            form = self._constructForm('POST', request.POST, instance=instance)
            
            form.hostQn = self.qn
            
            if form.is_valid():
                if returnType == 'ajax': 
                    return HttpResponse('not implemented')
                f = form.save()
                args[2] = f.id
                editURL = reverse('pimms.apps.qn.views.edit', args=args)   
                logging.debug('Successful edit post, redirecting to %s' %editURL)
                
                return HttpResponseRedirect(editURL)#(okURL)
            else:
                print 'ERRORS [%s]' %form.errors
        elif request.method == 'GET':
            form = self._constructForm('GET', instance=instance)
        
        constraints = self.constraints()
        if constraints:
            form.specialise(constraints)
                
        editURL = reverse('pimms.apps.qn.views.edit', args=args) 
                          
        return render_to_response(self.editHTML,
                                    {'form'    :form,
                                     'editURL' :editURL,
                                     'okURL'   :okURL,
                                     'tabs'    :tabs(request,self.qn,'Edit %s'%instance),
                                     'snippet_template':'qn/%s_snippet.html' %self.resource['type'],
                                     'resource': self.resource},
                                     context_instance=RequestContext(request))
                                                 
                                                 
    def delete(self,request,returnType):
        ''' Delete an item ... '''
        if self.target:
            okURL=reverse('pimms.apps.qn.views.%s'%returnType,
               args=(self.cid,self.resource['type'],self.target['type'],self.target['instance'].id,))
        else:
            okURL=reverse('pimms.apps.qn.views.%s'%returnType,
               args=(self.cid,self.resource['type'],))
        if request.method=='POST':
            if self.resource['id']<>'0':
                instance=self.resource['class'].objects.get(id=self.resource['id'])
                if instance.centre==self.centre: 
                    if 'confirmed' in request.POST:
                        success,related_objects=instance.delete()
                        if success:
                            return HttpResponseRedirect(okURL)
                        else:
                            # We shouldn't ever get here
                            return HttpResponseBadRequest('Invalid data request (somehow something is still linking to this object)')
                    else: 
                        success,related_objects=instance.delete(simulate=True)
                        if success:
                            url=request.path
                            return render_to_response('confirm_delete.html',
                                    {'klass':self.resource['type'],'url':url,'i':instance})
                        else:
                            # show the user the things they need to handle
                            return render_to_response('invalid_delete.html',
                                        {'klass':self.resource['type'],'instance':instance,'failed':related_objects})
        #all other cases are invalid      
        return HttpResponseBadRequest("Invalid delete request")
    
    def assign(self,request):
        ''' This method binds to the target resource, a number of the resources managed
        by this one. eg If this class is instantiated with resourceType = file, and
        this method is called with an instance (target) of some class, then this
        method will bind the chosen files to that target, and then return to that
        target view via targetURL. We provide targetType and targetID to allow 
        the construction of return URLs when we go to the editor ...'''
         
        title='Assign %s(s) to %s %s'%(self.resource['type'],self.target['type'],self.target['instance'])
        objects=self.objects()

        data=[(r.id,str(r)) for r in objects]
        
        # two possible forms could be used, multiple choice, or single choice.
        class AssignForm(forms.Form):
            ''' Used for producing a form for selection of multiple choices '''
            choose=forms.MultipleChoiceField(choices=data,
                          widget=forms.CheckboxSelectMultiple(), required=False)  
            
        class AssignOneForm(forms.Form):
            ''' Used for selecting just one option from a list '''
            choose=forms.ChoiceField(choices=data)
         
        showChoices=len(data)
        
        # We have two sorts of django attributes to deal with here,
        # foreign keys, and manytomany fields.
        target=self.target['instance'] 
        manager=target.__getattribute__(self.resource['attname'])
        
        # is it a manytomanyfield?
        many2many="<class 'django.db.models.fields.related.ManyRelatedManager'>"
        manyClass=str(type(manager))
        JustOne=(manyClass!=many2many)
        #need to get at the initial values and choose an appropriate form
        if JustOne:
            if manager is None: 
                initial=[]
            else: initial=manager.id
            ActualForm=AssignOneForm
        else:
            initial=[i.id for i in manager.get_query_set()]
            ActualForm=AssignForm
                          
        if request.method=='POST':
            rform=ActualForm(request.POST)
            if rform.is_valid():
                #now parse these up and assign to the resource
                if not JustOne:manager.clear()
                new=rform.cleaned_data['choose']
                if JustOne:
                    target.__setattr__(self.resource['attname'],objects.get(id=new))
                else:
                    for n in new:
                        r=objects.get(id=n)
                        manager.add(r)
                target.save()
                return HttpResponseRedirect(self.target['url'])
        elif request.method=='GET':
            #need to ensure that if there are none already chosen, we don't bind the form ...
            if initial==[]:
                rform=ActualForm()
            else:rform=ActualForm({'choose':initial})
                
        url=''
        
        #editURL and form used to add a new instance.
        editURL=reverse('pimms.apps.qn.views.edit',
            args=(self.cid,self.resource['type'],0,self.target['type'],self.target['instance'].id,'assign'))
        listURL=reverse('pimms.apps.qn.views.list',
            args=(self.cid,self.resource['type'],self.target['type'],self.target['instance'].id))
            
        return render_to_response(self.selectHTML,
            {'showChoices':showChoices,
                'rform':rform,
                'title':title,
                'form':self._constructForm('GET'),
                'editURL':editURL,'listURL':listURL,
                'editTemplate':'%s_snippet.html'%self.resource['type'],
                'tabs':tabs(request,self.cid,'Assign %s'%self.resource['type']),
                'chooseURL':url})
               
           
                
         
         