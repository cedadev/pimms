# -*- coding: utf-8 -*-
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'

from django.conf import settings

# get the cmip5 settings
#sys.path.append('/../../')
#sys.path.append('/../../pimms')
sys.path.append(settings.PROJECT_ROOT)
sys.path.append(os.path.join(settings.PROJECT_ROOT, "apps/qn"))
sys.path.append(os.path.join(settings.PROJECT_ROOT, "apps/vocabs"))

from pimms.apps.qn.models import Experiment
from pimms.apps.initialiser.XMLinitialiseQ import initialise
from pimms.apps.initialiser.ControlledModel import initialiseModel
from pimms.apps.initialiser.ControlledGrid import initialiseGrid
from pimms.apps.initialiser.initialiseRefs import initialiseRefs
from pimms.apps.initialiser.initialiseFiles import initialiseFiles
from pimms.apps.initialiser.initialiseVars import initialiseVars


# Initialise the Questionnaire
initialise()

# load cmip5 input files
initialiseFiles()

# load variables associated with cmip5 input files
initialiseVars()

# load cmip5 input references
initialiseRefs()

# create experiments
experimentDir = os.path.join(settings.PROJECT_ROOT, "static/data/experiments")
for f in os.listdir(experimentDir):
    if f.endswith('.xml'):
        x = Experiment.fromXML(os.path.join(experimentDir, f))

# initialise a model template
initialiseModel()

# initialise a grid template
initialiseGrid()