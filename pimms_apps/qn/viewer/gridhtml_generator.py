"""
HTML generator for different sections of a gridspec CIM instance.
"""

# Module imports.
from pimms_apps.qn.viewer.for_html import *
from pimms_apps.qn.viewer.common import *

# Module provenance info.
__author__="Gerry Devine"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 30, 2011 2:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Gerry Devine"
__email__ = "g.m.devine@reading.ac.uk"
__status__ = "Production"


#namespaces used within the CIM
cimns = 'http://www.purl.org/org/esmetadata/cim/1.5/schemas'
gmlns = 'http://www.opengis.net/gml/3.2'
gmdns = 'http://www.isotc211.org/2005/gmd'
gcons = 'http://www.isotc211.org/2005/gco'
xsins = 'http://www.w3.org/2001/XMLSchema-instance'


def get_grid_name(cimxml):
    """
    Get the gridspec shortname.
    """
    gridname =  cimxml.find('esmModelGrid/shortName')
    
    return gridname


def get_mgihtml(elemroot):
    """
    Manage html markup of main grid info
    """
    mgihtml = []
    mgihtml.append(begin_inner_acc_block('Overview Information'))
    
    #begin html block for main grid information
    mgihtml.append('<table class="acc_row">')

    #attach short name
    shortname = elemroot.findtext('esmModelGrid/shortName')
    mgihtml.append(viewer_tr('Short Name', shortname))
    
    #attach long name
    longname = elemroot.findtext('esmModelGrid/longName')
    mgihtml.append(viewer_tr('Long Name', longname))
    
    #attach description
    description = elemroot.findtext('esmModelGrid/description')
    mgihtml.append(viewer_tr('Description', description))
    
    #end html block for grid tile information
    mgihtml.append('</table>')
    mgihtml.append('<br/>')
    
    mgihtml.append(end_inner_acc_block())
    
    return mgihtml


def get_gtehtml(elemroot, gthtml):
    """
    Manage html markup of grid tile extent info
    """    
    #begin html block for main grid information
    gthtml.append('<table class="acc_row">')

    #attach latmin
    latmin = elemroot.findtext('latMin')
    gthtml.append(viewer_tr('Latitude Minimum', latmin))
    
    #attach latmax
    latmax = elemroot.findtext('latMax')
    gthtml.append(viewer_tr('Latitude Maximum', latmax))
    
    #attach lonmin
    lonmin = elemroot.findtext('lonMin')
    gthtml.append(viewer_tr('Longitude Minimum', lonmin))
    
    #attach lonmax
    lonmax = elemroot.findtext('lonMax')
    gthtml.append(viewer_tr('Longitude Maximum', lonmax))
    
    #end html block for grid tile information
    gthtml.append('</table>')
    gthtml.append('<br/>')
    
    return gthtml


def gt_iter(elemroot, gthtml):
    """
    Iterate through and harvest information on grid tiles
    """ 
    
    gthtml.append('<table class="acc_row">')
    #attach grid tile mnemonic
    gt_mnem = elemroot.findtext('mnemonic')
    gthtml.append(viewer_tr('Mnemonic', gt_mnem))
    
    #attach discretizationType
    gt_disc = elemroot.get('discretizationType')
    gthtml.append(viewer_tr('Discretization Type', gt_disc))
    
    #attach grid tile description
    gt_desc = elemroot.findtext('description')
    gthtml.append(viewer_tr('Description', gt_desc))
    
    gthtml.append('</table>')
    gthtml.append('<br/>')
    
    # attach grid tile extent block
    gthtml.append(begin_inner_acc_block('Grid Extent'))
    get_gtehtml(elemroot.find('extent'), gthtml)
    gthtml.append(end_inner_acc_block())
    
    return gthtml


def get_gthtml(elemroot):
    """
    Manage html markup of grid tiles
    """
    gridtiles = elemroot.findall('esmModelGrid/gridTile' )
    gthtml = []
    for tile in gridtiles:    
        gthtml.append(begin_inner_acc_block('Grid Tile'))
        gt_iter(tile, gthtml)
        gthtml.append(end_inner_acc_block())
    
    return gthtml


def main_grid_iter(elemroot, gridhtml):
    """
    Manage the iteration through and harvesting of CIM gridSpec sections
    """
    # find and mark up main grid info
    mgihtml = get_mgihtml(elemroot)
    gridhtml += mgihtml
    
    # find and mark up grid tile info
    gthtml = get_gthtml(elemroot)
    gridhtml += gthtml
      
    # find and mark up document information
    dihtml = get_dihtml(elemroot)
    gridhtml += dihtml
    
    # find and mark up citation information
    cithtml = get_cithtml(elemroot)
    gridhtml += cithtml
    
    return gridhtml


def get_gridhtml(cimxml):
    """
    Generate a block of html code to render a gridspec view.
    """
    #Get the grid name for the html heading
    gridname = get_grid_name(cimxml)
    
    gridhtml = []
    gridhtml.append(begin_inner_acc_block(gridname.text))
    #Iterate through the grid xml and harvest all required information
    main_grid_iter(cimxml, gridhtml)
    gridhtml.append(end_inner_acc_block())

    return gridhtml
