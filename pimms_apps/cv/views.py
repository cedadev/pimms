from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from pimms_apps.cv.forms import MMForm
from pimms_apps.cv.mindmap import checkMM, translateMM
from pimms_apps.cv.helpers import getcvurls
from pimms_apps.helpers import getsiteurls
from os.path import splitext


@login_required
def cvhome(request):
    '''Controller for cv app home page
    
    Acts as the mindmap file upload page. A user can decide whether or not to 
    ignore any warnings in the mindmap (i.e. only errors will halt translation 
    to xml)    
    '''
  
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getcvurls(urls) 
    except:
        raise Http404
      
   # import pdb; pdb.set_trace()
    if request.method == 'POST':
        mmform = MMForm(request.POST, request.FILES)
        if mmform.is_valid():
            # Grab the uploaded mindmap file
            mmfile = request.FILES['uploadedfile']
            # Check for any warnings/errors in the freemind mindmap   
            errors, warnings = checkMM(mmfile) 
            # Are warnings to be ignored?
            igWarnings = mmform.cleaned_data['igWarnings']
            
            if errors or (warnings and not igWarnings):   # generate an error/warnings report page
                return render_to_response('report.html', {'urls': urls, 
                                                               'errors': errors, 
                                                               'warnings': warnings}, 
                                       context_instance=RequestContext(request))
                
            else: #continue to translation
                translation = translateMM(mmfile)
                
                filename = mmfile.name.encode('utf8','ignore')
                basename = splitext(filename)[0]
                response = HttpResponse(translation, content_type='application/xml')
                response['Content-Disposition'] = 'attachment; filename=' + basename + '.xml'
                return response
#               mimetype='application/xml'
#               return HttpResponse(translation, mimetype)
                #return render_to_response('page/report.html', {'urls': urls, 
                #                                               'translation': translation}, 
                #                       context_instance=RequestContext(request))
                 
        else:
            # TODO: Need to put in better handling here
            return HttpResponseRedirect(urls['cvhome'])
    else:
        mmform = MMForm()      
    
    return render_to_response('cvhome.html', {'urls': urls, 'mmform': mmform},
                              context_instance=RequestContext(request))


@login_required
def about(request):
    '''Controller for app about page
    
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getcvurls(urls) 
    except:
        raise Http404
      
    return render_to_response('page/about.html', {'urls': urls},
                              context_instance=RequestContext(request))
