"""
helper functions for generic HTML code generation 
"""

# Module provenance info.
__author__="Gerry Devine"
__copyright__ = "Copyright 2011 - Metafor Project"
__date__ ="$Jun 29, 2010 5:52:22 PM$"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Gerry Devine"
__email__ = "g.m.devine@reading.ac.uk"
__status__ = "Production"


def viewer_tr(name, value):
    '''
    returns a html table row snippet for a name-value pair 
    '''
    htmlblock = []
    htmlblock.append('  <tr class="acc_row">')
    htmlblock.append('    <td class="accnametext">')
    htmlblock.append('      <p class="accnametext">%s</p>' %name)
    htmlblock.append('    </td>')
    htmlblock.append('    <td>')
    htmlblock.append('      <p class="accvaluetext">%s</p>' %value)
    htmlblock.append('    </td>')
    htmlblock.append('  </tr> ')
    
    html = "".join(htmlblock)
    return u'{0}'.format(html)


def begin_inner_acc_block(heading):
    '''
    returns a html snippet for beginning an inner accordion panel
    (paired with end_inner_acc_block)
    '''
    htmlblock = []
    htmlblock.append('<ul>')
    htmlblock.append('<li>')
    htmlblock.append('<h5>%s</h5>' %heading)
    htmlblock.append('<div class="inner">')
    
    html = "".join(htmlblock)
    return u'{0}'.format(html)


def end_inner_acc_block():
    '''
    ends a html snippet for beginning an inner accordian panel
    (paired with begin_inner_acc_block) 
    '''
    htmlblock = []
    
    htmlblock.append('</div>')
    htmlblock.append('</li>')
    htmlblock.append('</ul>')
    
    html = "".join(htmlblock)
    return u'{0}'.format(html)


def begin_outer_acc_block(heading):
    '''
    returns a html snippet for beginning an outer (top level) accordion panel
    (paired with end_outer_acc_block)
    '''
    htmlblock = []
    htmlblock.append('<div id="acc_wrapper">')
    htmlblock.append('<div id="content">')
    htmlblock.append('<div id="container">')
    htmlblock.append('<div id="main">')
    htmlblock.append('<ul class="accordion" id="acc1">')
    htmlblock.append('<li>')
    htmlblock.append('<h4 class="acc_docheader">Grid: %s </h4>' %heading )
    htmlblock.append('<div class="inner">')
    
    html = "".join(htmlblock)
    return u'{0}'.format(html)


def end_outer_acc_block():
    '''
    ends a html snippet for beginning an outer accordian panel
    (paired with begin_outer_acc_block) 
    '''
    htmlblock = []
    htmlblock.append('</div>')
    htmlblock.append('</li>')
    htmlblock.append('</ul>')
    htmlblock.append('</div>')
    htmlblock.append('</div>')
    htmlblock.append('</div>')
    htmlblock.append('</div>')
    htmlblock.append('<br/>')
    
    html = "".join(htmlblock)
    return u'{0}'.format(html)