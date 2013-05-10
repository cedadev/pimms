from pimms_apps.qn.models import Experiment
from pimms_apps.qn.qnsetup.XMLinitialiseQ import initialise
from pimms_apps.qn.qnsetup.ControlledModel import initialiseModel
from pimms_apps.qn.qnsetup.ControlledGrid import initialiseGrid
#from pimms_apps.qn.initialiser.initialiseRefs import initialiseRefs
#from pimms_apps.qn.initialiser.initialiseFiles import initialiseFiles
#from pimms_apps.qn.initialiser.initialiseVars import initialiseVars


def generate_qn(qn, cvlist, gridcv, explist):
    '''
    Top level questionnaire setup function
    '''
    
    # Initialise the Questionnaire
    initialise(qn)

    # load in experiments
    for exp in explist:
        Experiment.fromXML(qn, exp)

    # initialise a model template and upload supplied cvs
    initialiseModel(qn, cvlist)

    # initialise a grid template and upload supplied grid cv
    initialiseGrid(qn, gridcv)