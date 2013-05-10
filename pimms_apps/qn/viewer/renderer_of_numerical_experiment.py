"""
A concrete view over a cim instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms.apps.qn.viewer.base_renderer import RendererBase
from pimms.apps.qn.viewer.simhtml_generator import get_simrunhtml

# Module provenance info.
__author__="markmorgan"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 28, 2010 2:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Sebastien Denvil"
__email__ = "sdipsl@ipsl.jussieu.fr"
__status__ = "Production"


class RendererOfNumericalExperiment(RendererBase):
    """
    Manages rendering of a view over a cim numerical experiment.
    """

    @property
    def view_type(self):
        """
        Unique key identifying the view type.
        """
        return 'numericalExperiment'

    
    def render(self):
        """
        Renders the view in the relevant format/mode.
        """
        return u'TODO - render {0}'.format(self.view_type)
