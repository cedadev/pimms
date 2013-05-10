from django.core.urlresolvers import reverse


# set up generic urls
def genurls():
    '''Creates a dictionary of URL reversals for the CV app
    
    '''
    
    urls = {}
    urls['cvhome'] = reverse('cvhome', args=())
    
    return urls
  