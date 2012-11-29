'''
Helpers for CV application
'''

from django.core.urlresolvers import reverse


# set up generic urls
def getcvurls(urls):
    '''Append cv related urls to master dictionary
    
    '''
  
    urls['cvhome'] = reverse('cvhome', args=())
    
    return urls
