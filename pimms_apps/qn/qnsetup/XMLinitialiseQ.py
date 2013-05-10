# -*- coding: utf-8 -*-
#
##
## This file for all the initialisation that SHOULD come from XML but currently
## doesn't.
##
##

import os 
os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'

from django.conf import settings

from pimms_apps.qn.vocabs.cf import CFtable
from pimms_apps.qn.models import *
from pimms_apps.qn.utilities import atomuri
from pimms_apps.qn.vocabs.InputTransformations import properties
from pimms_apps.qn.vocabs.centres import loadCentres 

# tell the questionnaire that this is a cmip5 configuration.
# This allows us to do cmip5 specific things in the questionnaire
QuestionniareConfiguration='cmip5'

# this is the controlled vocabulary for realms:
# that is, the top level areas under the model definitions.

VocabList={'Realms':
     ('LandIce','Ocean','SeaIce','Atmosphere','OceanBiogeoChemistry',
     'AtmosphericChemistry','Aerosols','LandSurface'),
     
     # controlled vocabulary for file formats
     'FileFormats':('NetCDF','Grib','PP','Excel','Text','HDF','Other'),
             
    # this tuple should provide a controlled vocabulary for referenceTypes
    'ReferenceTypes':('Webpage','Online Refereed','Offline Refereed',
                      'Online Other','Offline Other'),

    'FreqUnits':('seconds','minutes','hours','days','months','years','decades'),

    # and these will support platforms
    'hardwareType':('Vector','Parallel','Beowulf'),
    'vendorType':('Cray Inc','Dell','Fujitsu','Hitachi','IBM','Intel','NEC','SGI','Sun Microsystems',
               'Appro International','Linux Networx','Self-made','Hewlett-Packard','Dawning',
               'Bull SA','T-Platforms','NEC/Sun','DALCO AG Switzerland','ClusterVision/Dell',
               'Koi Computers','Pyramid Computer','ACTION','ClusterVision/IBM','SKIF/T-Platforms',
               'Raytheon-Aspen Systems/Appro','Lenovo','NUDT','DELL\ACS','Dell/Sun/IBM','Other'),
    
    'compilerType':('Absoft','Intel','Lahey','NAG','Silverfrost','Portland PGI','Pathscale','Other'),
    
    'operatingSystemType':('Linux','AIX','Darwin','Unicos','Irix64','SunOS','Other'),

    #following extended from top500 site:
    'processorType':('NEC','Sparc','Intel IA-64','Intel EM64T','AMD X86_64',
                          'Other Intel','Other AMD','Other'),   
    'interconnectType':('Myrinet','Quadrics','Gigabit Ethernet','Infiniband','Mixed',
                        'NUMAlink','SP Switch','Cray Interconnect','Fat Tree','Other'),
    
    #geneology 
    'relations':('higherResoutionVersionOf', 
                 'lowerResolutionVersionOf', 
                 'laterVersionOf', 
                 'fixedVersionOf'),

    #types of conformance, just allow one.
    'ConformanceTypes':('Standard Config', 
                        'Via Inputs', 
                        'Via Model Mods', 
                        'Via Combination', 
                        'Not Conformant', 
                        'Not Applicable'),

    # types of modification
    'ModificationTypes':('ModelMod','InputMod'),
    # input requirements
    'InputTypes':('InitialCondition','BoundaryCondition','AncillaryFile'),
    # model modification types
    'ModelModTypes':('ParameterChange','CodeChange','Unused'),

    # types of numerical requirement 
    'NumReqTypes':('NumericalRequirement','BoundaryCondition','InitialCondition','SpatioTemporalConstraint','RequirementSet','OutputRequirement'),
    # should be used in spatio temporal constraints
    'SpatialResolutionTypes':('',),
    
    #ensembleTypes
    'EnsembleTypes':('Experiment Driven','Initial Condition','Perturbed Physics','Perturbed Boundary Conditions','Mixed'),
    
    #calendarTypes
    'CalendarTypes':('perpetualPeriod','realCalendar','daily-360'),
    
    #simulation relationship types
    'SimRelationships':('hasControlSimulation','extends','other','fixedVersionOf','usesSpinup'),
    
    #data relationship types
    'dataRelationships':('using','usingModifiedVersionOf'),
    }
    
    
def loadCF(qn):
     p = os.path.join('apps', 'qn', 'vocabs', 'cf-standard-name-table.xml')
     cf = CFtable(p)
     v = Vocab(qn=qn, uri='cf-standard-name-table.xml', name='CFStandardNames', version=cf.version)
     v.save()
     vu = Vocab(qn=qn, uri='cf-standard-name-table-units', name='CFStandardNameUnits', version=cf.version)
     vu.save()
     ulist=[]
     for e in cf.names:
         if e.units not in ulist:
            u = Term(vocab=vu, name=e.units)
            u.save()
            ulist.append(e.units)
         else:
            u = Term.objects.filter(name=e.units).get(vocab=vu)
         pp = PhysicalProperty(vocab=v, name=e.name, definition=e.description, units=u)
         pp.save()


def loadProperties(qn, args):
    for arg in args:
        defn, values = properties[arg]
        v = Vocab(qn=qn, uri=atomuri(), name=arg, definition=defn)
        v.save()
        
        for r, d in values:
            rv = Term(vocab=v, name=r, definition=d)
            rv.save()


def reloadVocab(key):
    ''' Used to reset vocabulariews '''
    vocab=Vocab.objects.get(name=key)
    for v in Term.objects.filter(vocab=vocab).order_by('id'):
        v.delete()
    vocab.delete()
    loadvocab(key)


def loadvocab(key, qn):
    ''' Used to load vocabularies '''
    
    v=Vocab(uri=atomuri(), name=key, qn=qn)
    v.save()
    values=VocabList[key]
    for r in values:
        rv=Term(vocab=v, name=r)
        rv.save()


def initialise(qn):
    '''This routine initialises the CMIP5 questionaire '''
    
    #start with initialising the centres:
    ##loadCentres()
            
    for k in VocabList: 
        loadvocab(k, qn)
    
    # now get the specialist vocabs
    # currently just coupling
    loadProperties(qn, ('InputTechnique', 'SpatialRegrid', 'TimeTransformation'))
    #loadCF(qn)
    
