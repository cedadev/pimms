'''
helpers for qn application
'''

from django.core.urlresolvers import reverse


# set up generic urls
def getqnurls(urls, qnname):
    '''Append qn related urls to master dictionary
    
    '''
  
    urls['qnhome'] = reverse('qnhome', args=(qnname))
    
    return urls
