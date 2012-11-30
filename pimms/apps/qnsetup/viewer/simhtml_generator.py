"""
HTML generator for different sections of a modelComponent CIM instance.
"""

# Module imports.
#import lxml
#from lxml import etree as et

# Module provenance info.
__author__="markmorgan"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 28, 2010 2:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Sebastien Denvil"
__email__ = "sdipsl@ipsl.jussieu.fr"
__status__ = "Production"


#namespaces used within the CIM
cimns = 'http://www.purl.org/org/esmetadata/cim/1.5/schemas'
gmdns = 'http://www.isotc211.org/2005/gmd'
gcons = 'http://www.isotc211.org/2005/gco'
xsins = 'http://www.w3.org/2001/XMLSchema-instance'


def get_sim_shortname(cimxml):
    """
    Get the simulation shortname.
    """
    return cimxml.find('shortName')

def get_mihtml(elemroot):
    """
    Manage html markup of main simulation level info
    """
    mihtml = []
    mihtml.append('<ul>')
    mihtml.append('<li>')
    mihtml.append('<h5>Overview Information</h5>')
    mihtml.append('<div class="inner">')

    # harvest required information from xml
    shortname = elemroot.find('shortName')
    longname = elemroot.find('longName')
    description = elemroot.find('description')
    simproj = elemroot.find('project')
    proj = simproj.get('value')
    authors = elemroot.find('authorsList/list')

    for mi in [shortname, longname, description]:
        if mi is not None:
            #tagminns = mi.tag.split(cimns + '}')[1]
            mihtml.append('            <table width=100%>')
            mihtml.append('                <tr class="acc_row">')
            mihtml.append('                    <td width = 20%>')
            mihtml.append('                        <p class="titletext">%s</p>' %mi.tag)
            mihtml.append('                    </td>')
            mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %mi.text)
            mihtml.append('                </tr> ')
            mihtml.append('            </table>')

    if proj is not None:
        mihtml.append('            <table width=100%>')
        mihtml.append('                <tr class="acc_row">')
        mihtml.append('                    <td width = 20%>')
        mihtml.append('                        <p class="titletext">Project</p>')
        mihtml.append('                    </td>')
        mihtml.append('                    <td><p class="bodytext">%s</p></td>' %proj)
        mihtml.append('                </tr> ')
        mihtml.append('            </table>')

    if authors is not None:
        mihtml.append('            <table width=100%>')
        mihtml.append('                <tr class="acc_row">')
        mihtml.append('                    <td width = 20%>')
        mihtml.append('                        <p class="titletext">Simulation Authors</p>')
        mihtml.append('                    </td>')
        mihtml.append('                    <td><p class="bodytext">%s</p></td>' %authors.text)
        mihtml.append('                </tr> ')
        mihtml.append('            </table>')

    mihtml.append('</div>')
    mihtml.append('</li>')
    mihtml.append('</ul>')

    return mihtml

def get_exphtml(elemroot):
    """
    Manage html markup of supported experiment info
    """
    exphtml = []
    exphtml.append('<ul>')
    exphtml.append('<li>')
    exphtml.append('<h5>Supporting Experiment</h5>')
    exphtml.append('<div class="inner">')

    # harvest required information from xml
    name = elemroot.find('supports/reference/name')
    expdocid = elemroot.find('supports/reference/id')
    expdocvers = elemroot.find('supports/reference/version')

    for info in [name, expdocid, expdocvers]:
        if info is not None:
            #tagminns = info.tag.split(cimns + '}')[1]
            exphtml.append('            <table width=100%>')
            exphtml.append('                <tr class="acc_row">')
            exphtml.append('                    <td width = 20%>')
            exphtml.append('                        <p class="titletext">%s</p>' %info.tag)
            exphtml.append('                    </td>')
            exphtml.append('                    <td><p class="bodytext">%s</p></td>'  %info.text)
            exphtml.append('                </tr> ')
            exphtml.append('            </table>')

    exphtml.append('</div>')
    exphtml.append('</li>')
    exphtml.append('</ul>')

    return exphtml


def rp_iter(elemroot, rphtml):
    """
    Iterate through and harvest information on responsible parties
    """
    cl = elemroot.find('{%s}role/{%s}CI_RoleCode' %(gmdns, gmdns))
    role = cl.get('codeListValue')

    #get individual name or organisation name
    ind_org_name = '{%s}individualName/{%s}CharacterString' %(gmdns, gcons)
    if elemroot.findtext(ind_org_name):
        name = elemroot.findtext(ind_org_name)
    else:
        name = elemroot.findtext('{%s}organisationName/{%s}CharacterString' %(gmdns, gcons))

    address = elemroot.findtext('{%s}contactInfo/{%s}CI_Contact/{%s}address/{%s}CI_Address/{%s}deliveryPoint/{%s}CharacterString' %(gmdns, gmdns, gmdns, gmdns, gmdns, gcons))
    email = elemroot.findtext('{%s}contactInfo/{%s}CI_Contact/{%s}address/{%s}CI_Address/{%s}electronicMailAddress/{%s}CharacterString' %(gmdns, gmdns, gmdns, gmdns, gmdns, gcons))

    rphtml.append('            <table width=100%>')
    rphtml.append('                <tr class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Role</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %role)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Name</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %name)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Address</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %address)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Email</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %email)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('            </table>')
    rphtml.append('            <br/>')

    return rphtml

def get_rphtml(elemroot):
    """
    Manage html markup of responsible party info
    """
    respParties = elemroot.findall('responsibleParty')
    rphtml = []
    if respParties:
        rphtml.append('<ul>')
        rphtml.append('<li>')
        rphtml.append('<h5>Responsible Parties</h5>')
        rphtml.append('<div class="inner">')
        for party in respParties:
            rp_iter(party, rphtml)
        rphtml.append('</div>')
        rphtml.append('</li>')
        rphtml.append('</ul>')

    return rphtml

def cit_iter(elemroot, cithtml):
    """
    Iterate through and harvest information on citations
    """
    #get citation title
    cit_title = elemroot.findtext('{%s}title/{%s}CharacterString' %(gmdns, gcons))
    #get citation type
    pfc = elemroot.find('{%s}presentationForm/{%s}CI_PresentationFormCode' %(gmdns, gmdns))
    cit_type = pfc.get('codeListValue')
    #get citation reference
    cit_ref = elemroot.findtext('{%s}collectiveTitle/{%s}CharacterString' %(gmdns, gcons))
    #get citation location
    cit_loc = elemroot.findtext('{%s}otherCitationDetails/{%s}CharacterString' %(gmdns, gcons))

    #create html block for citation information
    cithtml.append('            <table width=100%>')
    cithtml.append('                <tr class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Title</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_title)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Type</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_type)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Reference</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_ref)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Location</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_loc)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('            </table>')
    cithtml.append('            <br/>')

    return cithtml

def get_cithtml(elemroot):
    """
    Manage html markup of citation info
    """
    citations = elemroot.findall('citation')
    cithtml = []
    if citations:
        cithtml.append('<ul>')
        cithtml.append('<li>')
        cithtml.append('<h5>Citations</h5>')
        cithtml.append('<div class="inner">')
        for citation in citations:
            cit_iter(citation, cithtml)
        cithtml.append('</div>')
        cithtml.append('</li>')
        cithtml.append('</ul>')

    return cithtml

def conf_iter(elemroot, confhtml):
    """
    Iterate through and harvest information on conformances
    """
    conformant = elemroot.get('conformant')
    conformby = elemroot.get('type')
    req = elemroot.findtext('requirement/reference/description' )
    description = elemroot.findtext('description')

    confhtml.append('            <table width=100%>')
    confhtml.append('                <tr class="acc_row">')
    confhtml.append('                    <td width = 20%>')
    confhtml.append('                        <p class="titletext">Requirement</p>')
    confhtml.append('                    </td>')
    confhtml.append('                    <td>')
    confhtml.append('                      <p class="bodytext">%s</p>' %req)
    confhtml.append('                    </td>')
    confhtml.append('                </tr> ')
    confhtml.append('                <tr class="acc_row">')
    confhtml.append('                    <td width = 20%>')
    confhtml.append('                        <p class="titletext">Conformant?</p>')
    confhtml.append('                    </td>')
    confhtml.append('                    <td>')
    confhtml.append('                      <p class="bodytext">%s</p>' %conformant)
    confhtml.append('                    </td>')
    confhtml.append('                </tr> ')
    confhtml.append('                <tr class="acc_row">')
    confhtml.append('                    <td width = 20%>')
    confhtml.append('                        <p class="titletext">Conforms by</p>')
    confhtml.append('                    </td>')
    confhtml.append('                    <td>')
    confhtml.append('                      <p class="bodytext">%s</p>' %conformby)
    confhtml.append('                    </td>')
    confhtml.append('                </tr> ')
    if description is not None:
        confhtml.append('                <tr class="acc_row">')
        confhtml.append('                    <td width = 20%>')
        confhtml.append('                        <p class="titletext">description</p>')
        confhtml.append('                    </td>')
        confhtml.append('                    <td>')
        confhtml.append('                      <p class="bodytext">%s</p>' %description)
        confhtml.append('                    </td>')
        confhtml.append('                </tr> ')
    confhtml.append('            </table>')
    confhtml.append('            <br/>')

    return confhtml

def get_confhtml(elemroot):
    """
    Manage html markup of conformance info
    """
    confs = elemroot.findall('conformance/conformance')
    confhtml = []
    if confs:
        confhtml.append('<ul>')
        confhtml.append('<li>')
        confhtml.append('<h5>Conformance information</h5>')
        confhtml.append('<div class="inner">')
        for conf in confs:
            conf_iter(conf, confhtml)
        confhtml.append('</div>')
        confhtml.append('</li>')
        confhtml.append('</ul>')

    return confhtml

def get_dihtml(elemroot):
    """
    Manage html markup of cim document info
    """
    doc_id = elemroot.find('documentID')
    doc_version = elemroot.find('documentVersion' )
    doc_date = elemroot.find('documentCreationDate')
    doc_author = elemroot.find('documentAuthor/{%s}individualName/{%s}CharacterString' %(gmdns, gcons))
    
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
            dihtml.append('                        <p class="titletext">%s</p>' %di.tag)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    for di in [doc_author]:
        if di is not None:
            tagminns = di.tag.split(gcons + '}')[1]
            dihtml.append('            <table width=100%>')
            dihtml.append('                <tr class="acc_row">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' %tagminns)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    dihtml.append('</div>')
    dihtml.append('</li>')
    dihtml.append('</ul>')

    return dihtml

def main_simrun_iter(elemroot, simrunhtml):
    """
    Manage the iteration through and harvesting of CIM simulationRun sections
    """
    # find and mark up top level component info
    mihtml = get_mihtml(elemroot)
    simrunhtml += mihtml

    # find and mark up the linked experiment info
    exphtml = get_exphtml(elemroot)
    simrunhtml += exphtml

    # find and mark up responsible party info
    rphtml = get_rphtml(elemroot)
    simrunhtml += rphtml

    # find and mark up conformance information
    confhtml = get_confhtml(elemroot)
    simrunhtml += confhtml

    # find and mark up document information
    dihtml = get_dihtml(elemroot)
    simrunhtml += dihtml
    
    return simrunhtml

def get_simrunhtml(cimxml):
    """
    Generate a block of html code to render a simulationRun view.
    """
    #Get the simulation name for the html heading
    simshortname = get_sim_shortname(cimxml)

    #Generate the outer html code
    simrunhtml=[]
    simrunhtml.append('<div id="acc_wrapper">')
    simrunhtml.append('    <div id="content">')
    simrunhtml.append('        <div id="container">')
    simrunhtml.append('            <div id="main">')
    simrunhtml.append('<ul class="accordion" id="acc1">')
    simrunhtml.append('<li>')
    simrunhtml.append('<h4 class="acc_docheader">Simulation: %s</h4>' %simshortname.text)
    simrunhtml.append('<div class="inner">')

    #Iterate through the simulationRun xml and harvest all required information
    main_simrun_iter(cimxml, simrunhtml)

    #Complete the outer html code
    simrunhtml.append('</div>')
    simrunhtml.append('</li>')
    simrunhtml.append('</ul>')
    simrunhtml.append('</div>')
    simrunhtml.append('</div>')
    simrunhtml.append('</div>')
    simrunhtml.append('</div>')
    simrunhtml.append('<br/>')


    return simrunhtml