"""
A concrete view over a cim instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms.apps.qn.viewer.base_renderer import RendererBase
from pimms.apps.qn.viewer.datahtml_generator import get_datahtml


class RendererOfDataObject(RendererBase):
    """
    Manages rendering of a view over a cim data object.
    """

    @property
    def view_type(self):
        """
        Unique key identifying the view type.
        """
        return 'dataObject'


    def render(self):
        """
        Renders the view in the relevant format/mode.
        """
        html_block = "".join(get_datahtml(self.cim_xml))
        return u'{0}'.format(html_block)