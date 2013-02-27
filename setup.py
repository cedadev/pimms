from setuptools import setup, find_packages
import sys, os
import os.path as op

here = op.dirname(__file__)

# Import version from the top-level package
sys.path[:0] = here
from pimms import __version__
README = open(op.join(here, 'README')).read()

setup(name='pimms',
      version=__version__,
      description='The PIMMS Model Metadata stack',
      long_description=README,
      url='http://www.ceda.ac.uk/projects/pimms/',
      packages=find_packages(),
      include_package_data=True,
      )
