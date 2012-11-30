import os
import csv

os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'

from django.conf import settings

from pimms.apps.qn.models import *

logging=settings.LOG


def initialiseRefs():
    ''' 
    This routine initialises the database with some obvious files for 
    boundary conditoins etc 
    '''
    
    filepath = os.path.join(settings.PROJECT_ROOT, "static/data/References/Refs_CSV.csv")
    CSVinfo = csv.reader(open(filepath), delimiter=';', quotechar='|')
    
    # this is the vocab that we always use for reference types:
    v=Vocab.objects.get(name='ReferenceTypes')
    # loop over all rerences in spreadsheet
    for row in CSVinfo:
        print row
        logging.debug(', '.join(row))
        name,citation,link=tuple(row)
        # find out what refrence type
        myreftype='Online Refereed'
        try:
            refType=Term.objects.filter(vocab=v).get(name=myreftype)
        except:
            logging.info('Ignoring reference %s'%', '.join(row))
            break  # leave the loop
        # find the other things: name, citation, link    
        r=Reference(name=name,
                    citation=citation,
                    link=link,
                    refTypes=v,
                    refType=refType)
        try:
            r.save()
        except:
            logging.info('Unable to save reference %s'%name)
        # temporary 2 lines
        def __unicode__(self):
            return
    
if __name__=="__main__":
    initialiseRefs()