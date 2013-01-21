# -*- coding: utf-8 -*-
#import os
#import sys
#
#os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'

from django.conf import settings

from pimms.apps.qn.models import Experiment
from pimms.apps.qn.initialiser.XMLinitialiseQ import initialise
from pimms.apps.qn.initialiser.ControlledModel import initialiseModel
from pimms.apps.qn.initialiser.ControlledGrid import initialiseGrid
#from pimms.apps.qn.initialiser.initialiseRefs import initialiseRefs
#from pimms.apps.qn.initialiser.initialiseFiles import initialiseFiles
#from pimms.apps.qn.initialiser.initialiseVars import initialiseVars


def generate_qn(qn, cvlist, gridcv, explist):
    '''
    Top level questionnaire setup function
    '''
    
    # Initialise the Questionnaire
    initialise(qn)

    # load in experiments
    for exp in explist:
        Experiment.fromXML(qn, exp)

    # initialise a model template
    initialiseModel(qn, cvlist)

    # initialise a grid template
    initialiseGrid(qn, gridcv)