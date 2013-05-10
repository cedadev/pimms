"""
A view of a cim instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms_apps.qn.viewer.view_exception import ViewException
from pimms_apps.qn.viewer.base_renderer import VIEW_FORMAT_HTML
from pimms_apps.qn.viewer.base_renderer import VIEW_FORMAT_PDF
from pimms_apps.qn.viewer.base_renderer import VIEW_FORMAT_XML
from pimms_apps.qn.viewer.base_renderer import VIEW_MODE_FULL
from pimms_apps.qn.viewer.base_renderer import VIEW_MODE_PARTIAL
from pimms_apps.qn.viewer.renderer_of_data_object import RendererOfDataObject
from pimms_apps.qn.viewer.renderer_of_document_set import RendererOfDocumentSet
from pimms_apps.qn.viewer.renderer_of_model_component import RendererOfModelComponent
from pimms_apps.qn.viewer.renderer_of_numerical_experiment import RendererOfNumericalExperiment
from pimms_apps.qn.viewer.renderer_of_simulation_run import RendererOfSimulationRun
from pimms_apps.qn.viewer.renderer_of_gridspec import RendererOfGridspec
from pimms_apps.qn.viewer.renderer_of_platform import RendererOfPlatform


# Dictionary ofsupported renderers.
_renderers = {}
_renderers['dataObject'] = RendererOfDataObject
_renderers['CIMDocumentSet'] = RendererOfDocumentSet
_renderers['modelComponent'] = RendererOfModelComponent
_renderers['numericalExperiment'] = RendererOfNumericalExperiment
_renderers['simulationRun'] = RendererOfSimulationRun
_renderers['gridspec'] = RendererOfGridspec
_renderers['platform'] = RendererOfPlatform


def _deserialize_cim_xml(cim_xml_source):
    """
    Deserializes cim instance to an etree .
    """
    # Error if none.
    if cim_xml_source is None:
        raise ViewException("CIM instance is undefined.")
    # Etree elements.
    elif isinstance(cim_xml_source, et._Element):
        return cim_xml_source
    # Etree element trees.
    elif isinstance(cim_xml_source, et._ElementTree):
        return cim_xml_source.getroot()
    else:
        # Files or URLs.
        try:
            return et.parse(cim_xml_source)
        except Exception:
            # Strings.
            if isinstance(cim_xml_source, basestring):
                try:
                    return et.fromstring(cim_xml_source)
                except Exception:
                    raise ViewException("Invalid xml string.")
            else:
                raise ViewException("Unsupported cim_instance type, must be either a string, file, url or etree.")


def _get_document_type(cim_xml):
    """
    Returns cim document type.
    """
    # Strips out namespace.
    result = cim_xml.tag
    #ns_end = result.find(u"}")
    #if ns_end > 0:
    #    result = result.replace(result[0:ns_end + 1], "")
    return result


def _get_renderer(cim_xml, format, mode):
    """
    Returns cim document view renderer.
    """
    doc_type = _get_document_type(cim_xml)
    try:
        renderer = _renderers[doc_type]
    except KeyError:
        raise ViewException("Unsupported cim document type :: {0}".format(doc_type))
    return renderer(cim_xml, format, mode)


def render_view(cim_xml, format=VIEW_FORMAT_HTML, mode=VIEW_MODE_FULL):
    '''
    Renders a CIM instance view.
    '''
    
    # Deserialise cim xml (i.e. etree Element).
    #cim_xml = _deserialize_cim_xml(cim_xml_source)

    # Derive renderer to use.
    renderer = _get_renderer(cim_xml, format, mode)

    # Return rendering result.
    return renderer.render()