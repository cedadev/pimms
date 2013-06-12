"""
HTML generators for sections common amongst CIM documents.
"""

# Module imports.
from pimms_apps.qn.viewer.for_html import *

# Module provenance info.
__author__="Gerry Devine"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 30, 2011 3:52:22 PM$"
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


def cit_iter(elemroot, cithtml):
    """
    Harvests information on citations and creates html accordion block
    """
    #begin html block for citation information
    cithtml.append('<table>')
    
    #attach citation abbreviation
    cit_abbrev = elemroot.findtext('{%s}title/{%s}CharacterString' 
                                  %(gmdns, gcons))
    cithtml.append(viewer_tr('Abbreviation', cit_abbrev))
    
    #attach citation date
    cit_date = elemroot.findtext('{%s}date/{%s}CI_Date/{%s}date/{%s}Date' 
                                 %(gmdns, gmdns, gmdns, gcons))
    cithtml.append(viewer_tr('Date', cit_date))
    
    #attach frequency
    cit_pres = elemroot.find('{%s}presentationForm/{%s}CI_PresentationFormCode' 
                             %(gmdns, gmdns))
    if cit_pres is not None:
        cit_pres = cit_pres.get('codeListValue')
    else: 
        cit_pres = ''
    cithtml.append(viewer_tr('Frequency', cit_pres))
    
    #attach citation reference    
    cit_ref = elemroot.findtext('{%s}collectiveTitle/{%s}CharacterString' 
                                  %(gmdns, gcons))
    cithtml.append(viewer_tr('Reference', cit_ref))
    
    #end html block for citation information
    cithtml.append('</table>')
    cithtml.append('<br/>')

    return cithtml


def get_cithtml(elemroot):
    """
    Manage html markup of citations info
    """
    citations = elemroot.findall('{%s}esmModelGrid/{%s}citationList/'\
                                 '{%s}citation' %(cimns, cimns, cimns))
    cithtml = []
    if citations:
        cithtml.append(begin_inner_acc_block('Citations'))
        for citation in citations:
            cit_iter(citation, cithtml)
        cithtml.append(end_inner_acc_block())

    return cithtml


def get_dihtml(elemroot):
    """
    Manage html markup of cim document info
    """
    dihtml = []
    dihtml.append(begin_inner_acc_block('Document Information'))
    
    #begin html block for grid document information
    dihtml.append('<table class="acc_row">')
    
    #attach document id
    doc_id = elemroot.findtext('{%s}documentID' %cimns)
    dihtml.append(viewer_tr('Document ID', doc_id))
    
    #attach document version
    doc_version = elemroot.findtext('{%s}documentVersion' %cimns)
    dihtml.append(viewer_tr('Document Version', doc_version))
    
    #attach document date                            
    doc_date = elemroot.findtext('{%s}documentCreationDate' %cimns)
    dihtml.append(viewer_tr('Document Creation Date', doc_date))
    
    #attach document author    
    doc_author = elemroot.findtext('{%s}documentAuthor/{%s}individualName/'\
                               '{%s}CharacterString' %(cimns, gmdns, gcons))
    dihtml.append(viewer_tr('Document Author', doc_author))
    
    #end html block for grid document information
    dihtml.append('</table>')
    dihtml.append('<br/>')
    
    dihtml.append(end_inner_acc_block())

    return dihtml