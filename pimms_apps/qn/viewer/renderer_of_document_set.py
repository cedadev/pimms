"""
A concrete view over a cim instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms_apps.qn.viewer.base_renderer import RendererBase
from pimms_apps.qn.viewer.docsethtml_generator import get_docsethtml

# Module provenance info.
__author__="markmorgan"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 28, 2010 2:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Sebastien Denvil"
__email__ = "sdipsl@ipsl.jussieu.fr"
__status__ = "Production"


class RendererOfDocumentSet(RendererBase):
    """
    Manages rendering of a view over a cim document set.
    """

    @property
    def view_type(self):
        """
        Unique key identifying the view type.
        """
        return 'documentSet'
    

    def render(self):
        """
        Renders the view in the relevant format/mode.
        """
        html_block = "".join(get_docsethtml(self.cim_xml))
        return u'{0}'.format(html_block)
