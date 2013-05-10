"""
The set of view exception classes.
"""

# Module imports.


# Module provenance info.
__author__="markmorgan"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 28, 2010 2:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Sebastien Denvil"
__email__ = "sdipsl@ipsl.jussieu.fr"
__status__ = "Production"


class ViewException(Exception):
    """
    The standard view exception class.
    """

    def __init__(self, message):
        self.message = message


    def __str__(self):
        return "METAFOR VIEW EXCEPTION : {0}".format(repr(self.message))
