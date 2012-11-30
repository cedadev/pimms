# -*- coding: utf-8 -*-
#
# This file contains the textural values for the coupling vocabularies
# Note that not all these vocabs need to be actually used.
# Enough information to establish SKOS if we want, I hope ...
# BNL, based on ticket 256.
#

author='Metafor Team'
email='badc@rl.ac.uk'
version='2010-01-15-01'
definition='These terms describe the properties of input transformations'
label='Input Transformations'
alternateLabel='Coupling Properties'

properties={
    'InputTechnique':('Technical method or tool for providing inputs',
        [('Files',''),
         ('OASIS3',''),
         ('OASIS4',''),
         ('FMS',''),
         ('ESMF',''),
         ('CCSM Flux coupler',''),
         ('MCT',''),
         ('Shared Memory',''),
         ('File',''),
         ('Other',''),
         ]),
    
    'SpatialRegrid':('Method used to spatially interpolate a field from one grid (source grid) to another (target grid)',
        [('Conservative','The area integral of the coupling field is conserved between the source and the target grid',),
         ('Non-Conservative','No properties are conserved in the regridding'),
         ('None Used','No spatial regridding is carried out'),
         ]),
    
    'SpatialRegridDim':('Dimensionality of the regridding',
        [('N/A','Not Applicable'),
         ('Two Dimensional','Regridding using only two dimensions on interface'),
         ('Three Dimensional','Three dimensional data has been used, whether or not the coupling field is two or three dimensional'),
         ('Other','Some other technique'),
         ]),
     
    'SpatialNumericAccuracy':('Accuracy of the numerics used for spatial regridding',
        [('First-Order','First order numerics'),
         ('Second-Order','Second order numerics'),
         ('Third-Order','Third order numerics'),
         ('Unknown','Unknown numerical accuracy'),
         ('Other','Other'),
         ]),
         
    'TimeTransformation':('How the source grid data was manipulated for input to the target grid (whether before or after the spatial regridding)',
        [('Exact','The two grids used common timesteps'),
         ('TimeAverage','Some temporal average of source grid data was used'),
         ('TimeAccumulation','Source grid data was averaged over time'),
         ('FirstAvailable','The first available source grid data was used (typically for ensemble initial conditions overwriting file date and times'),
         ('LastAvailable','The last available source grid data was used'),
         ('TimeInterpolation','Source grid data was interpolated to the target grid time'),
         ('Other','Some other temporal transformation was used'),
         ]),
        }