from pimms.apps.qn.models import Experiment
from pimms.apps.qn.qnsetup.XMLinitialiseQ import initialise
from pimms.apps.qn.qnsetup.ControlledModel import initialiseModel
from pimms.apps.qn.qnsetup.ControlledGrid import initialiseGrid
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

    # initialise a model template and upload supplied cvs
    initialiseModel(qn, cvlist)

    # initialise a grid template and upload supplied grid cv
    initialiseGrid(qn, gridcv)