from xml.etree import ElementTree as ET
import unittest

def clean(s):
    return s.strip()

class CFentry:
    def __init__(self,elem):
        ''' Take an element tree element from the cf-standard-name table and resolve to a python object '''
        self.name=elem.attrib['id']
        self.units=clean(elem.find('canonical_units').text or '')
        self.description=clean(elem.find('description').text or '')
       
class CFtable:
    ''' Provide the cf standard names vocabulary '''
    def __init__(self,path):
        ''' Currently instantiate the vocabulary from a file '''
        et=ET.parse(path)
        root=et.getroot()
        entries=root.findall('entry')
        self.names=[]
        self.version=clean(root.find('version_number').text)
        for entry in entries:
            cfe=CFentry(entry)
            self.names.append(cfe)
         
class TestFunctions(unittest.TestCase):
    def testCF(self):
        import os
        d='vocabs'
        p=os.path.join('apps', d,'cf-standard-name-table.xml')
        cf=CFtable(p)

