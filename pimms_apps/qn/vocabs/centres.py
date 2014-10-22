from pimms_apps.qn.models import *

import uuid

CENTRES=(
             ('BADC','UK National Centre for Atmospheric Science',('HiGEM1.2')),
             ('NCAS','UK National Centre for Atmospheric Science',('HiGEM1.2')),
             ('NCAR','US National Centre for Atmospheric Research',('CCSM4(H)','CCM4(M)')),
             ('MOHC','UK Met Office Hadley Centre',('HadCM3','HadCM3Q','HadGEM2-ES')),
             ('NOAA-GFDL','Geophysical Fluid Dynamics Laboratory',('GFDL-HIRAM','GFDL-ESM2G','GFDL-ESM2M','GFDL-CM3','GFDL-CM2.1')),
             ('IPSL','Institut Pierre Simon Laplace',('IPSL-CM6','IPSL-CM5')),
             ('MPI-M','Max Planck Institute for Meteorology',('ECHAM5-MPIOM')), 
             ('CMIP5','Dummy Centre used to hold model template',('dum')),
             ('1. Example','Dummy Centre used to hold examples',('dum')),
             ('NCC','Norwegian Climate Centre',('NorESM')),
             ('MRI','Meteorological Research Institute',('MRI-CGM3','MRI-ESM1','MRI-AM20km','MRI-AM60km')),
             ('MIROC','University of Tokyo, National Institute for Environmental Studies, and Japan Agency for Marine-Earth Science and Technology',('MIROC4.2(M)','(MIRO4.2(H)','MIROC3.2(M)','MIROC-ESM')),
             ('INM','Russian Institute for Numerical Mathematics',('INMCM4.0')),
             ('NIMR-KMA','Korean National Institute for Meteorological Research',('HadGEM2-AO')),
             ('LASG-CESS','Institute of Atmospheric Physics, Chinese Academy of Sciences	China',('FGOALS-S2.0','FGOALS-G2.0','FGOALS-gl')),
             ('CSIRO-QCCCE','Queensland Climate Change Centre of Excellence and Commonwealth Scientific and Industrial Research Organisation',('CSIRO-Mk3.5A')),
             ('CNRM-CERFACS','Centre National de Recherches Meteorologiques / Centre Europeen de Recherche et de Formation Avancee en Calcul Scientifique',('CNRM-CM5')),
             ('CCCMA','Canadian Centre for Climate Modelling and Analysis',('CanESM2')),
             ('CSIRO-BOM','Centre for Australian Weather and Climate Research',('ACCESS',)),
             ('NASA-GISS','NASA Goddard Institute for Space Studies USA',('')),
             ('BCC','Beijing Climate Center, China Meteorological Administration',('BCC-CSM')),
             ('2. Test Centre','Test area',('dum')),
             ('EC-EARTH','EC-EARTH consortium',('EC-Earth')),
             ('NSF-DOE-NCAR','Community Climate System Model',('')),
             ('CMCC','Centro Euro-Mediterraneo per I Cambiamenti Climatici',('')),
             ('GCESS','College of Global Change and Earth System Science, Beijing Normal University',('')),
             ('FIO','The First Institute of Oceanography, SOA, China',('')),
             ('RSMAS','University of Miami - RSMAS',('')),
             ('NASA-GMAO','NASA Global Modeling and Assimilation Office',('')),
             ('LASG-IAP','LASG, Institute of Atmospheric Physics, Chinese Academy of Sciences',('')),
             ('NCEP','National Centres for Environmental Prediction',(''))
        )
def loadCentres():
    for centre in CENTRES:
        u = str(uuid.uuid1())
        c = Centre(abbrev=centre[0], name=centre[1], uri=u)
        c.isOrganisation = True
        c.save()
        #and give each of them an unknown user to play with
        rp = ResponsibleParty(name='Unknown',
                              abbrev='Unknown',
                              address='Erehwon',
                              email='u@foo.bar',
                              uri=str(uuid.uuid1()))
  #                            centre=c)
        rp.save()
