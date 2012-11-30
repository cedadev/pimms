"""
HTML generator for different sections of a dataObject CIM instance.
"""

# Module imports.
import lxml
from lxml import etree as et

from pimms.apps.qn.viewer.for_html import *
from pimms.apps.qn.viewer.common import *

# Module provenance info.
__author__="Gerry Devine"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 28, 2011 2:52:22 PM$"
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


def get_data_name(cimxml):
    """
    Get the data acronym.
    """
    #return cimxml.find('{%s}acronym' %cimns)
    dataname =  cimxml.find('content/topic/name')
    datastatus = cimxml.get('dataStatus')
    
    if dataname is not None:
        return dataname.text, datastatus
    else:
        return '', datastatus


def get_mdihtml(elemroot):
    """
    Manage html markup of main data level info
    """
    mdihtml = []
    mdihtml.append('<ul>')
    mdihtml.append('<li>')
    mdihtml.append('<h5>Overview Information</h5>')
    mdihtml.append('<div class="inner">')

    #First get non-attribute information
    dataacc = elemroot.find('acronym')
    datadescription = elemroot.find('description')

    for mdi in [dataacc, datadescription]:
        if mdi is not None:
            #tagminns = mdi.tag.split(cimns + '}')[1]
            mdihtml.append('            <table width=100%>')
            mdihtml.append('                <tr class="acc_row">')
            mdihtml.append('                    <td width = 20%>')
            mdihtml.append('                        <p class="titletext">%s</p>' 
                           %mdi.tag)
            mdihtml.append('                    </td>')
            mdihtml.append('                    <td><p class="bodytext">%s</p>'\
                           '</td>'  %mdi.text)
            mdihtml.append('                </tr> ')
            mdihtml.append('            </table>')

    mdihtml.append('</div>')
    mdihtml.append('</li>')
    mdihtml.append('</ul>')

    return mdihtml


def get_cnthtml(elemroot):
    """
    Manage html markup of data content info
    """
    #get name
    cntname = elemroot.find('content/topic/name')
    #get standard name
    cntstdname = elemroot.find('content/topic/standardName')
    if cntstdname is not None:
        cntstdname = cntstdname.get('value')
    else:
        cntstdname = ''
    #get units
    cntunits = elemroot.find('content/topic/unit')
    if cntunits is not None:
        cntunits = cntunits.get('value')
    else:
        cntunits = ''
    #get description
    cntdesc = elemroot.find('content/topic/description')
    #get aggregation
    cntagg = elemroot.find('content/aggregation')
    #get frequency
    cntfreq = elemroot.find('content/frequency')
    if cntfreq is not None:
        cntfreq = cntfreq.get('value')
    else:
        cntfreq = ''
    
    cnthtml = []
    cnthtml.append('<ul>')
    cnthtml.append('<li>')
    cnthtml.append('<h5>Data Content</h5>')
    cnthtml.append('<div class="inner">')
    for cnt in [cntname, cntdesc]:
        if cnt is not None:
            #tagminns = cnt.tag.split(cimns + '}')[1]
            cnthtml.append('            <table width=100%>')
            cnthtml.append('                <tr class="acc_row">')
            cnthtml.append('                    <td width = 20%>')
            cnthtml.append('                        <p class="titletext">%s</p>' 
                           %cnt.tag)
            cnthtml.append('                    </td>')
            cnthtml.append('                    <td><p class="bodytext">%s</p>'\
                           '</td>'  %cnt.text)
            cnthtml.append('                </tr> ')
            cnthtml.append('            </table>')
    
    cnthtml.append('            <table width=100%>')
    cnthtml.append('                <tr class="acc_row">')
    cnthtml.append('                    <td width = 20%>')
    cnthtml.append('                        <p class="titletext">Standard Name'\
                   '</p>')
    cnthtml.append('                    </td>')
    cnthtml.append('                    <td><p class="bodytext">%s</p></td>'  
                   %cntstdname)
    cnthtml.append('                </tr> ')
    cnthtml.append('            </table>')
    cnthtml.append('            <table width=100%>')
    cnthtml.append('                <tr class="acc_row">')
    cnthtml.append('                    <td width = 20%>')
    cnthtml.append('                        <p class="titletext">Units</p>')
    cnthtml.append('                    </td>')
    cnthtml.append('                    <td><p class="bodytext">%s</p></td>'  
                   %cntunits)
    cnthtml.append('                </tr> ')
    cnthtml.append('            </table>')
    if cntagg is not None:
        cnthtml.append('            <table width=100%>')
        cnthtml.append('                <tr class="acc_row">')
        cnthtml.append('                    <td width = 20%>')
        cnthtml.append('                        <p class="titletext">'\
                       'Aggregation </p>')
        cnthtml.append('                    </td>')
        cnthtml.append('                    <td><p class="bodytext">%s</p></td>'  
                       %cntagg.text)
        cnthtml.append('                </tr> ')
        cnthtml.append('            </table>')
    if cntfreq is not None:
        cnthtml.append('            <table width=100%>')
        cnthtml.append('                <tr class="acc_row">')
        cnthtml.append('                    <td width = 20%>')
        cnthtml.append('                        <p class="titletext">Frequency</p>')
        cnthtml.append('                    </td>')
        cnthtml.append('                    <td><p class="bodytext">%s</p></td>'  
                       %cntfreq)
        cnthtml.append('                </tr> ')
        cnthtml.append('            </table>')
    
    cnthtml.append('</div>')
    cnthtml.append('</li>')
    cnthtml.append('</ul>')

    return cnthtml


def get_exthtml(elemroot):
    """
    Manage html markup of data extent info
    """    
    exthtml = []
    exthtml.append('<ul>')
    exthtml.append('<li>')
    exthtml.append('<h5>Data Extent</h5>')
    exthtml.append('<div class="inner">')
    
    #render geographic boundings  
    exthtml.append('<ul>')
    exthtml.append('<li>')
    exthtml.append('<h5>Geographic Extent</h5>')
    exthtml.append('<div class="inner">')  
    for bd in ['westBoundLongitude', 'eastBoundLongitude', 'southBoundLatitude', 
               'northBoundLatitude']:
        bounding = elemroot.find('extent/{%s}geographicElement/'\
                                 '{%s}EX_GeographicBoundingBox/'\
                                 '{%s}%s/{%s}Decimal' %(gmdns, gmdns, 
                                                        gmdns, bd, gcons))
        if bounding is not None:
            exthtml.append('            <table width=100%>')
            exthtml.append('                <tr class="acc_row">')
            exthtml.append('                    <td width = 20%>')
            exthtml.append('                        <p class="titletext">%s</p>' 
                           %bd)
            exthtml.append('                    </td>')
            exthtml.append('                    <td><p class="bodytext">'\
                           '%s</p></td>'  %bounding.text)
            exthtml.append('                </tr> ')
            exthtml.append('            </table>')    

    exthtml.append('</div>')
    exthtml.append('</li>')
    exthtml.append('</ul>')
    
    #render temporal info  
    exthtml.append('<ul>')
    exthtml.append('<li>')
    exthtml.append('<h5>Temporal Extent</h5>')
    exthtml.append('<div class="inner">')  
    for pos in ['beginPosition', 'endPosition']:
        position = elemroot.find('extent/{%s}temporalElement/'\
                                 '{%s}EX_TemporalExtent/{%s}extent/'\
                                 '{%s}TimePeriod/{%s}%s' %(gmdns, 
                                  gmdns, gmdns, gmlns, gmlns, pos))
        if position is not None:
            exthtml.append('            <table width=100%>')
            exthtml.append('                <tr class="acc_row">')
            exthtml.append('                    <td width = 20%>')
            exthtml.append('                        <p class="titletext">%s'\
                           '</p>' %pos)
            exthtml.append('                    </td>')
            exthtml.append('                    <td><p class="bodytext">%s</p>'\
                           '</td>'  %position.text)
            exthtml.append('                </tr> ')
            exthtml.append('            </table>')    

    exthtml.append('</div>')
    exthtml.append('</li>')
    exthtml.append('</ul>')
    
    
    
    exthtml.append('</div>')
    exthtml.append('</li>')
    exthtml.append('</ul>')

    return exthtml


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
    for di in [doc_author]:
        if di is not None:
            #tagminns = di.tag.split(gcons + '}')[1]
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
    dihtml.append('</div>')
    dihtml.append('</li>')
    dihtml.append('</ul>')

    return dihtml


def get_cdhtml(elemroot):
    """
    Manage html markup of child data objects
    """
    childDatas=elemroot.findall('childObject/dataObject')
    cdhtml=[]
    if childDatas:
        cdhtml.append(begin_inner_acc_block('Child Data Objects'))
        for cd in childDatas:
            dataname = cd.find('content/topic/name')                
            cdhtml.append('<ul>')
            cdhtml.append('<li>')
            if dataname is not None:
                cdhtml.append('<h5>%s</h5>' %dataname.text)
            else:
                cdhtml.append('<h5>(Empty name)</h5>')
            cdhtml.append('<div class="inner">')
            main_data_iter(cd, cdhtml)
            cdhtml.append('</div>')
            cdhtml.append('</li>')
            cdhtml.append('</ul>')
        cdhtml.append(end_inner_acc_block())

    return cdhtml


def main_data_iter(elemroot, datahtml):
    """
    Manage the iteration through and harvesting of CIM dataObject sections
    """
    # find and mark up top level data info
    mdihtml = get_mdihtml(elemroot)
    datahtml += mdihtml

    # find and mark up content information
    cnthtml = get_cnthtml(elemroot)
    datahtml += cnthtml
    
    # find and mark up extent information
    exthtml = get_exthtml(elemroot)
    datahtml += exthtml
    
    # find and mark up citation information
    cithtml = get_cithtml(elemroot)
    datahtml += cithtml
    
    # find and mark up child data objects
    cdhtml = get_cdhtml(elemroot)
    datahtml += cdhtml
    
    # find and mark up document information
    dihtml = get_dihtml(elemroot)
    datahtml += dihtml
    
    return datahtml


def get_datahtml(cimxml):
    """
    Generate a block of html code to render a dataObject view.
    """
    #Get the data acronym name for the html heading
    dataname, datastatus = get_data_name(cimxml)
    
    #Generate the outer html code
    datahtml=[]
    datahtml.append('<div id="acc_wrapper">')
    datahtml.append('    <div id="content">')
    datahtml.append('        <div id="container">')
    datahtml.append('            <div id="main">')
    datahtml.append('<ul class="accordion" id="acc1">')
    datahtml.append('<li>')
    datahtml.append('<h4 class="acc_docheader">Data: %s (Status: %s)</h4>' 
                    %(dataname, datastatus))
    datahtml.append('<div class="inner">')

    #Iterate through the data xml and harvest all required information
    main_data_iter(cimxml, datahtml)

    #Complete the outer html code
    datahtml.append('</div>')
    datahtml.append('</li>')
    datahtml.append('</ul>')
    datahtml.append('</div>')
    datahtml.append('</div>')
    datahtml.append('</div>')
    datahtml.append('</div>')
    datahtml.append('<br/>')

    return datahtml