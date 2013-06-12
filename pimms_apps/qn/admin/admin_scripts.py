'''

Functions for use in the admin suite

Created on 6 Sep 2011

@author: gerarddevine
'''


import os
import sys

# putting project and application into sys.path  
sys.path.insert(0, os.path.expanduser('..\qn'))
sys.path.insert(1, os.path.expanduser('..\..\cmip5q'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from pimms_apps.qn.models import *


#*******************************************************************************
# Settings used within this code
testCentres = ['1. Example', '2. Test Centre']
origCentre = Centre.objects.get(abbrev='MOHC')
#targetCentre = Centre.objects.get(abbrev='1. Example')
origSim = 'piControl'
#*******************************************************************************


def copyRPToNewCen(sourceRP, targetCentre):
    """
    Copy a responsible party from one centre to another centre (targetcentre)
    """
    logging.debug('***** Copying Responsible Party *****') 
    
    # Check that the RP doesn't already exist, in which case do nothing     
    rps = ResponsibleParty.objects.filter(
            centre=targetCentre, abbrev=sourceRP.abbrev)
    if not rps:
        rp = ResponsibleParty(isOrganisation = sourceRP.isOrganisation,
                              name = sourceRP.name,
                              webpage = sourceRP.webpage,
                              abbrev = sourceRP.abbrev,
                              email = sourceRP.email,
                              address = sourceRP.address,
                              uri = atomuri(),
                              centre = targetCentre,
                              )
        rp.save()
    
        logging.debug('***** Completed responsible party copying *****')
    
        return rp
    
    else:
        logging.debug('***** Responsible party already existed*****')
        return rps[0]
    

def copyPlatToNewCen(sourcePlat, targetCentre):
    """
    Copy a platform from one centre to another centre
    """
    logging.debug('***** Copying Platform *****')
    
    # Retrieve and copy platform responsible parties
    platContact = copyRPToNewCen(sourcePlat.contact) 
    
    p = Platform(abbrev = sourcePlat.abbrev,
                 title = sourcePlat.title + ' (Example version)',
                 centre = targetCentre,   
                 contact = platContact,                      
                 compiler = sourcePlat.compiler,
                 compilerVersion = sourcePlat.compilerVersion,
                 vendor = sourcePlat.vendor,
                 maxProcessors = sourcePlat.maxProcessors,
                 coresPerProcessor = sourcePlat.coresPerProcessor,
                 operatingSystem = sourcePlat.operatingSystem,
                 processor = sourcePlat.processor,
                 hardware = sourcePlat.hardware, 
                 interconnect = sourcePlat.interconnect,
                 isDeleted = False,
                 uri = atomuri())
    p.save()
    
    logging.debug('***** Completed Platform copying *****')
    
    return p


def copyRefToNewCen(sourceRef, targetCentre):
    """
    Copy a reference from one centre to another centre (targetcentre)
    """
    logging.debug('***** Copying Reference *****') 
    
    # Check that the RP doesn't already exist, in which case do nothing     
    refs = Reference.objects.filter(
            centre=targetCentre, name=sourceRef.name)
    if not refs:
        ref = Reference(name = sourceRef.name,
                        citation = sourceRef.citation,
                        link = sourceRef.link,
                        refType = sourceRef.refType,
                        centre = targetCentre,
                        )
        ref.save()
    
        logging.debug('***** Completed Reference copying *****')
    
        return ref
    
    else:
        logging.debug('***** Reference already existed*****')
        return refs[0]
    
    
def copyPIToNewCen(sourcePI):
    """
    Copy parameter group information to the new model component 
    """
    logging.debug('***** Copying parameter information *****') 
    
    pgroup = ParamGroup(name=sourcePI.name)
    pgroup.save()
    
    logging.debug('***** Completed parameter information *****') 
    
    
def copyCompToNewCen(sourceComp, targetCentre, model=None, realm=None):
    """
    Copy a model from one centre to another centre
    """ 
    logging.debug('***** Copying Model *****')
    
    # Retrieve and copy platform responsible parties
    if sourceComp.author:
        compAuthor = copyRPToNewCen(sourceComp.author, targetCentre)
    else:
        compAuthor = None
    if sourceComp.funder:
        compFunder = copyRPToNewCen(sourceComp.funder, targetCentre)
    else:
        compFunder = None
    if sourceComp.contact:
        compContact = copyRPToNewCen(sourceComp.contact, targetCentre)
    else:
        compContact = None      
    
    m = Component(
              abbrev = sourceComp.abbrev,
              title = sourceComp.title + ' (Example centre version)',
              centre = targetCentre,
              documentVersion = sourceComp.documentVersion,
              description = sourceComp.description,
              validErrors = sourceComp.validErrors,
              numberOfValidationChecks = sourceComp.numberOfValidationChecks,
              isComplete = sourceComp.isComplete,
              created = sourceComp.created,
              updated = sourceComp.updated,
              scienceType = sourceComp.scienceType,
              implemented = sourceComp.implemented,
              visited = sourceComp.visited,
              controlled = sourceComp.controlled,
              isRealm = sourceComp.isRealm,
              isModel = sourceComp.isModel,
              isParamGroup = sourceComp.isParamGroup,
              yearReleased = sourceComp.yearReleased,
              otherVersion = sourceComp.otherVersion,
              isDeleted = sourceComp.isDeleted,
              author = compAuthor,
              funder = compFunder,
              contact = compContact, 
              uri = atomuri()
              )    
    m.save() 
    
    # now handle the associated references
    for r in sourceComp.references.all().order_by('id'):
        ref = copyRefToNewCen(r, targetCentre)
        m.references.add(ref)
    
    m.save()
    
    # now sort out the links to parent model/realm    
    if model is None:
        if sourceComp.isModel:
            model = m
        else:
            raise ValueError('Deep copy called with invalid model arguments')
    elif realm is None:
        if sourceComp.isRealm:
            realm = m
        else:
            raise ValueError('Deep copy called with invalid realm arguments')
    m.model = model
    m.realm = realm
    
    m.save()
    
    # copy across all child component information
    for c in sourceComp.components.all().order_by('id'):
        cc = copyCompToNewCen(c, targetCentre, model=m.model, realm=m.realm)
        
        m.components.add(cc)
    
    # copy across all parameter information
    for p in sourceComp.paramGroup.all().order_by('id'): 
        m.paramGroup.add(p.copy())
        
    # and deal with the component inputs too ..
    inputset = ComponentInput.objects.filter(owner=sourceComp).order_by('id')
    for i in inputset: 
        i.makeNewCopy(m)
    m.save()
    
    logging.debug('***** Completed Model copying *****')
    
    return m


def getDuplicatesForSim(s, origcoupling):
    ''' 
    Make a copy of self, and associate with a simulation
    '''
    cg = CouplingGroup(component = s.numericalModel, 
                       simulation = s)
    cg.save()
    
    cg.original = cg
    cg.save()
    
    #can't do the many to manager above, need to do them one by one
    for af in origcoupling.associatedFiles.all().order_by('id'):
        cg.associatedFiles.add(af)
        
    # now copy all the individual couplings associated with this group
    '''
    cset = self.coupling_set.all().order_by('id')
    for c in cset: 
        c.copy(new)
        
    return new
    '''


def copyToNewCen():
    """
    Copy a full simulation from one centre to the targetCentre
    """
    logging.debug('***** Copying Simulation *****')
    
    # 1. Get the simulation to copy (with origCentre and origSim meaning only 
    #    one can be returned)
    sourceSim = Simulation.objects.filter(centre=origCentre, 
                                          isDeleted=False).get(abbrev=origSim)
    
    # 2. Retrieve the platform used in this simulation and copy it
    sourcePlat = sourceSim.platform
    newPlat = copyPlatToNewCen(sourcePlat)
            
    # 3. Retrieve the model used in this simulation and copy it 
    sourceComp = sourceSim.numericalModel
    newMod = copyCompToNewCen(sourceComp)
              
    s = Simulation(abbrev = sourceSim.abbrev, 
                 title = sourceSim.title + ' (Example Version)', 
                 contact = sourceSim.contact, 
                 author = sourceSim.author, 
                 funder = sourceSim.funder,
                 description = sourceSim.description, 
                 authorList = sourceSim.authorList,
                 uri = atomuri(),
                 experiment = sourceSim.experiment, 
                 numericalModel = newMod,
                 ensembleMembers = sourceSim.ensembleMembers, 
                 platform = newPlat,
                 drsMember = sourceSim.drsMember, 
                 centre = targetCentre)
    s.save()
    
    #now we need to get all the other stuff related to this simulation
    # every simulation has it's own date range:
    s.duration = sourceSim.duration.copy()
    
    for mm in sourceSim.inputMod.all().order_by('id'):
        s.inputMod.add(mm)
    for mm in sourceSim.codeMod.all().order_by('id'):
        s.codeMod.add(mm)
    
    s._resetIO()
    
    s.save()
    
    # Get the current couplings for this simulation:
    myCouplings = CouplingGroup.objects.filter(component=\
        sourceSim.numericalModel).filter(simulation=sourceSim).order_by('id')
    for coupling in myCouplings:
        # Having to do this manually as opposed to using questionnaire code as
        # we need to use the new component created
        getDuplicatesForSim(s, coupling)


def delElem(elem):
    """
    Sets a passed element, e.g. component/grid to be marked as isDeleted 
    """
    assert hasattr(elem, 'isDeleted'), ("{0} is not of a type that can be "
                                        "marked isDeleted").format(elem)
    elem.isDeleted = True
    elem.save()


def clearCentre(cent):
    """
    Grab models, grids etc and send them off to be marked isDeleted OR delete
    in situ
    """
    # First those to be marked isDeleted
    for block in [Component, Grid, Simulation, Platform]:
        elems = block.objects.filter(centre=cent)
        for elem in elems:
            delElem(elem)
            
    # Now those that are actually physically deleted
    for block in [Reference, DataContainer, ResponsibleParty]:
        block.objects.filter(centre=cent).delete()


def emptyTestArea():
    '''
    Delete all entered information in the given testCentres
    '''
    logging.debug('***** START: Beginning deletion of test area centre '
                   'information *****')
    for cenabbrev in testCentres:
        cent = Centre.objects.get(abbrev=cenabbrev)
        clearCentre(cent)
    logging.debug('***** END: Completed deletion of test area centre '
                   'information *****')


def tidyTestArea():
    """
    Tidy up the test area of the cmip5 questionnaire by:
    1. clearing out all info in test and example centres
    2. copying updated information to example centre
    """
    logging.debug('***** START: Beginning tidy-up of test area centres *****')
        
    emptyTestArea()
    copyToNewCen()
            
    logging.debug('***** END: Completed tidy-up of test area centres *****')
        
           
if __name__ == '__main__':
    tidyTestArea()