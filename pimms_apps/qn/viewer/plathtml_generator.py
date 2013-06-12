"""
HTML generator for different sections of a dataObject CIM instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms_apps.qn.viewer.for_html import *
from pimms_apps.qn.viewer.common import *

# Module provenance info.
__author__="Gerry Devine"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Aug 08, 2011 2:52:22 PM$"
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


def get_plat_name(cimxml):
    """
    Get the platform shortname.
    """
    #return cimxml.find('{%s}acronym' %cimns)
    platname =  cimxml.find('shortName')
    
    return platname


def get_mpihtml(elemroot):
    """
    Manage html markup of main platform level info
    """
    mpihtml = []
    mpihtml.append('<ul>')
    mpihtml.append('<li>')
    mpihtml.append('<h5>Overview Information</h5>')
    mpihtml.append('<div class="inner">')

    #First get non-attribute information
    platsname = elemroot.find('shortName')
    platlname = elemroot.find('longName')
    if platlname is not None:
        platlnametext = platlname.text
    else:
        platlnametext = ''
    description = elemroot.find('description')
    if description is not None:
        descriptiontext = description.text
    else:
        descriptiontext = ''
        
    contact = elemroot.find('contact/abbreviation')


    mpihtml.append('          <table width=100%>')
    mpihtml.append('            <tr class="acc_row">')
    mpihtml.append('              <td width = 20%>')
    mpihtml.append('                <p class="titletext">Short Name</p>')
    mpihtml.append('              </td>')
    mpihtml.append('              <td><p class="bodytext">%s</p></td>' %platsname.text)
    mpihtml.append('            </tr> ')
    mpihtml.append('            <tr class="acc_row">')
    mpihtml.append('              <td width = 20%>')
    mpihtml.append('                <p class="titletext">Long Name</p>')
    mpihtml.append('              </td>')
    mpihtml.append('              <td><p class="bodytext">%s</p></td>' %platlnametext)
    mpihtml.append('            </tr> ')
    mpihtml.append('            <tr class="acc_row">')
    mpihtml.append('              <td width = 20%>')
    mpihtml.append('                <p class="titletext">Description</p>')
    mpihtml.append('              </td>')
    mpihtml.append('              <td><p class="bodytext">%s</p></td>' %descriptiontext)
    mpihtml.append('            </tr> ')
    mpihtml.append('            <tr class="acc_row">')
    mpihtml.append('              <td width = 20%>')
    mpihtml.append('                <p class="titletext">Contact</p>')
    mpihtml.append('              </td>')
    mpihtml.append('              <td><p class="bodytext">%s</p></td>' %contact.text)
    mpihtml.append('            </tr> ')
    mpihtml.append('          </table>')


    mpihtml.append('</div>')
    mpihtml.append('</li>')
    mpihtml.append('</ul>')

    return mpihtml


def get_mihtml(elemroot):
    """
    Manage html markup of machine info
    """
    #get machine name
    mname = elemroot.find('unit/machine/machineName')
    
    #get machine hardware type
    mhardware = elemroot.find('unit/machine/machineSystem')
    
    #get operating system
    mos = elemroot.find('unit/machine/machineOperatingSystem')
    if mos is not None:
        mosname = mos.get('value')
    else:
        mosname = ''
    
    #get vendor
    mvendor = elemroot.find('unit/machine/machineVendor')
    if mvendor is not None:
        mvendname = mvendor.get('value')
    else:
        mvendname = ''
    
    #get machine interconnect
    minterc = elemroot.find('unit/machine/machineInterconnect')
    if minterc is not None:
        minterconnect = minterc.get('value')
    else:
        minterconnect = ''
    
    #get max processors
    mmaxp = elemroot.find('unit/machine/machineMaximumProcessors')
    
    #get cores per processor
    mcpp = elemroot.find('unit/machine/machineCoresPerProcessor')
    if mcpp is not None:
        mcppvalue = minterc.get('value')
    else:
        mcppvalue = ''
    
    #get processor type
    mproctype = elemroot.find('unit/machine/machineProcessorType')
    if mproctype is not None:
        mpt = mproctype.get('value')
    else:
        mpt = ''
        
    #get compiler
    compiler = elemroot.find('unit/compiler/compilerName')
    #get compiler version
    compVers = elemroot.find('unit/compiler/compilerVersion')
       
       
    mihtml = []
    mihtml.append('<ul>')
    mihtml.append('<li>')
    mihtml.append('<h5>Machine information</h5>')
    mihtml.append('<div class="inner">')
            
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Machine Name</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mname.text)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Machine Hardware</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mhardware.text)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Machine Vendor</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mvendname)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Compiler</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %compiler.text)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Compiler Version</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %compVers.text)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Operating System</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mosname)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Maximum Processors</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mmaxp.text)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Cores per Processor</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %mcppvalue)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Processor Type</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>' %mpt)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('            <table width=100%>')
    mihtml.append('              <tr class="acc_row">')
    mihtml.append('                <td width = 20%>')
    mihtml.append('                  <p class="titletext">Interconnect Type</p>')
    mihtml.append('                </td>')
    mihtml.append('                <td><p class="bodytext">%s</p></td>'  %minterconnect)
    mihtml.append('                </tr> ')
    mihtml.append('            </table>')
    
    mihtml.append('</div>')
    mihtml.append('</li>')
    mihtml.append('</ul>')

    return mihtml


def get_dihtml(elemroot):
    """
    Manage html markup of cim document info
    """
    doc_id = elemroot.find('documentID')
    doc_version = elemroot.find('documentVersion')
    doc_date = elemroot.find('documentCreationDate')
    doc_author = elemroot.find('documentAuthor/{%s}individualName/'\
                               '{%s}CharacterString' %(gmdns, gcons))
    
    dihtml = []
    dihtml.append('<ul>')
    dihtml.append('<li>')
    dihtml.append('<h5>Document Information</h5>')
    dihtml.append('<div class="inner">')
    for di in [doc_id, doc_version, doc_date]:
        if di is not None:
            #tagminns = di.tag.split(cimns + '}')[1]
            dihtml.append('            <table width=100%>')
            dihtml.append('                <tr class="acc_row">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' 
                          %di.tag)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p>'\
                          '</td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    for di in [doc_author,]:
        if di is not None:
            #tagminns = di.tag.split(gcons + '}')[1]
            dihtml.append('            <table width=100%>')
            dihtml.append('                <tr class="acc_row">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">'\
                          'Document author</p>')
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p>'\
                                               '</td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    dihtml.append('</div>')
    dihtml.append('</li>')
    dihtml.append('</ul>')

    return dihtml


def main_plat_iter(elemroot, plathtml):
    """
    Manage the iteration through and harvesting of CIM platform sections
    """
    # find and mark up top level platform info
    mpihtml = get_mpihtml(elemroot)
    plathtml += mpihtml

    # find and mark up machine information
    mihtml = get_mihtml(elemroot)
    plathtml += mihtml
    
    # find and mark up document information
    dihtml = get_dihtml(elemroot)
    plathtml += dihtml
    
    return plathtml


def get_plathtml(cimxml):
    """
    Generate a block of html code to render a platform view.
    """
    #Get the platform shortname for the html heading
    platname = get_plat_name(cimxml)
    
    #Generate the outer html code
    plathtml=[]
    plathtml.append('<div id="acc_wrapper">')
    plathtml.append('    <div id="content">')
    plathtml.append('        <div id="container">')
    plathtml.append('            <div id="main">')
    plathtml.append('<ul class="accordion" id="acc1">')
    plathtml.append('<li>')
    plathtml.append('<h4 class="acc_docheader">Platform: %s </h4>' 
                    %(platname.text))
    plathtml.append('<div class="inner">')

    #Iterate through the plat xml and harvest all required information
    main_plat_iter(cimxml, plathtml)

    #Complete the outer html code
    plathtml.append('</div>')
    plathtml.append('</li>')
    plathtml.append('</ul>')
    plathtml.append('</div>')
    plathtml.append('</div>')
    plathtml.append('</div>')
    plathtml.append('</div>')
    plathtml.append('<br/>')

    return plathtml