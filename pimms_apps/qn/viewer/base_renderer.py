"""
Information common to all cim document views.
"""

# Module imports.
import abc
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

import lxml
from lxml import etree as et

from pimms_apps.qn.viewer.view_exception import ViewException

# Supported view formats.
VIEW_FORMAT_HTML = u"html"
VIEW_FORMAT_XML = u"xml"
VIEW_FORMAT_PDF = u"pdf"

# Supported view modes.
VIEW_MODE_FULL = "full"
VIEW_MODE_PARTIAL = "partial"


class RendererBase(object):
    """
    Encapsulates information common to all cim document views.
    """
    # Abstract Base Class module - see http://docs.python.org/library/abc.html
    __metaclass__ = ABCMeta

    def __init__(self, cim_xml, format=VIEW_FORMAT_HTML, mode=VIEW_MODE_FULL):
        """
        Constructor.
        """
        # ... set cim_xml;
        if isinstance(cim_xml, et._Element) == False:
            raise ViewException("Cim xml representation, must be \
                                 an instance of etree.Element.")
        self._cim_xml = cim_xml       
        # ... set view format;
        if format != VIEW_FORMAT_HTML and \
           format != VIEW_FORMAT_XML and \
           format != VIEW_FORMAT_PDF:
            raise ViewException("Unsupported view format :: {0}".format(format))
        self._view_format = format
        # ... set view mode;
        if mode != VIEW_MODE_FULL and \
           mode != VIEW_MODE_PARTIAL:
            raise ViewException("Unsupported view mode :: {0}".format(mode))
        self._view_mode = mode


    @abstractproperty
    def view_type(self):
        """
        Unique key identifying the view type.
        """
        pass


    @property
    def view_format(self):
        """
        The mode to render (html, xml, pdf ...etc.).
        """
        return self._view_format


    @property
    def view_mode(self):
        """
        The mode to render (full, partial ...etc.).
        """
        return self._view_mode


    @property
    def cim_xml(self):
        """
        CIM xml against which a view is to be rendered.
        """
        return self._cim_xml


    @abstractmethod
    def render(self):
        """
        Renders the view in the relevant format/mode.
        """
        pass