"""
A concrete view over a cim instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms.apps.qn.viewer.base_renderer import RendererBase
from pimms.apps.qn.viewer.modelhtml_generator import get_modelhtml


cimns = 'http://www.metaforclimate.eu/cim/1.4'

class RendererOfModelComponent(RendererBase):
    """
    Manages rendering of a view over a cim model.
    """

    @property
    def view_type(self):
        """
        Unique key identifying the view type.
        """
        return 'modelComponent'


    def render(self):
        """
        Renders the view in the relevant format/mode.
        """
        html_block = "".join(get_modelhtml(self.cim_xml))
        return u'{0}'.format(html_block)

