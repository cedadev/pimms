# -*- coding: utf-8 -*-
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'

from django.conf import settings

# get the cmip5 settings
#sys.path.append('/../../')
#sys.path.append('/../../pimms')
#sys.path.append(settings.PROJECT_ROOT)
#sys.path.append(os.path.join(settings.PROJECT_ROOT, "apps/qn"))
#sys.path.append(os.path.join(settings.PROJECT_ROOT, "apps/vocabs"))

from pimms.apps.qn.models import Experiment
from pimms.apps.qn.initialiser.XMLinitialiseQ import initialise
#from pimms.apps.qn.initialiser.ControlledModel import initialiseModel
#from pimms.apps.qn.initialiser.ControlledGrid import initialiseGrid
#from pimms.apps.qn.initialiser.initialiseRefs import initialiseRefs
#from pimms.apps.qn.initialiser.initialiseFiles import initialiseFiles
#from pimms.apps.qn.initialiser.initialiseVars import initialiseVars



def generate_qn(cvlist, explist):
    '''
    '''
    
    # Initialise the Questionnaire
    initialise()

    # load cmip5 input files
    #initialiseFiles()
    
    # load variables associated with cmip5 input files
    #initialiseVars()
    
    # load cmip5 input references
    #initialiseRefs()

    # load in experiments
    #experimentDir = os.path.join(settings.PROJECT_ROOT, "static/data/experiments")
    #for f in os.listdir(experimentDir):
    #    if f.endswith('.xml'):
    for exp in explist:
            Experiment.fromXML(exp)

    # initialise a model template
    #initialiseModel()

    # initialise a grid template
    #initialiseGrid()