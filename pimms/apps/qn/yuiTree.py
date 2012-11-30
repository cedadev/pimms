#
# Some code to support the navigation of model components 
#
from pimms.apps.qn.models import *
        
class ComponentFamily:
    ''' Used to provide a django template friendly structure for component heirarchy '''
    def __init__(self,me):
        ''' Initialise for a specific component '''
        self.me=me.id
        self.ancestors=[]
        self.siblings=[]
        self.children=[m.id for m in me.components.all().order_by('id')]
        # Now build up a family tree
        self.__getFamily(me)
        
    def __getFamily(self,component):
        ''' Get my family tree '''
        parents=Component.objects.filter(components=component.id).order_by('id')
        if len(parents)==0: return 
        parent=parents[0]
        self.siblings=[i.id for i in parent.components.all().order_by('id')]
        self.siblings.remove(component.id)
        self.__getFogies(parent)
        
    def __getFogies(self,parent):
        ''' Get the parentage of the parents '''
        self.ancestors.insert(0,parent.id)
        parents=Component.objects.filter(components=parent.id).order_by('id')
        if len(parents)==0: return 
        parent=parents[0]
        self.__getFogies(parent)
        

class GridFamily:
    ''' Used to provide a django template friendly structure for grid heirarchy '''
    def __init__(self,me):
        ''' Initialise for a specific grid '''
        self.me=me.id
        self.ancestors=[]
        self.siblings=[]
        self.children=[g.id for g in me.grids.all().order_by('id')]
        # Now build up a family tree
        self.__getFamily(me)
        
    def __getFamily(self,grid):
        ''' Get my family tree '''
        parents=Grid.objects.filter(grids=grid.id)
        if len(parents)==0: return 
        parent=parents[0]
        self.siblings=[i.id for i in parent.grids.all().order_by('id')]
        self.siblings.remove(grid.id)
        self.__getFogies(parent)
        
    def __getFogies(self,parent):
        ''' Get the parentage of the parents '''
        self.ancestors.insert(0,parent.id)
        parents=Grid.objects.filter(grids=parent.id)
        if len(parents)==0: return 
        parent=parents[0]
        self.__getFogies(parent)

        
class yuiTree2:
    ''' Provides an ordered list view of the component heirarchy, for use
    by a yuiTree to control component visibility '''
    def __li(self,e,i,a,ok=0):
        url=self.baseURL.replace(self.template,'%s'%i)
        ok1,ok2={0:('',''),1:('[',']')}[ok] #used to denote hanging chads (see debug)
        cc={1:' class="open"',0:''}[i==self.family.me]
        return '<li%s>%s<a href="%s"%s>%s</a>%s\n'%(e,ok1,url,cc,a,ok2)
    
    def __init__(self,component_id,baseURL,top='model',template='+EDID+'):
        component=Component.objects.get(pk=component_id)
        self.baseURL=baseURL
        self.template=template
        self.html='<ul>\n'
        self.found=[]
        self.family=ComponentFamily(component)
        self.expanders=self.family.ancestors
        self.expanders.append(self.family.me)
        #clist=Component.objects.filter(scienceType='model').filter(centre=component.centre_id)
        clist=Component.objects.filter(scienceType='model').filter(model=component.model).order_by('id')
        for c in clist: self.__walk(c)
        #self.__debug()
        self.html+='</ul>\n'
    
    def __walk(self,component):
        ''' Show me and my children'''
        children=component.components.all().order_by('id')
        # we don't .order_by('abbrev') because we want the order we loaded them in ...
        classes=[]
        if component.id in self.expanders: classes.append('expanded')
        if component.id == self.family.me: classes.append('highlight') 
        cstring=''
        for i in classes:cstring+='%s '%i
        if cstring<>'': cstring=' class="%s"'%cstring[0:-1]
        self.html+=self.__li(cstring,component.id,component.abbrev)
        self.found.append(component.id)
        if len(children)==0: return
        # now, if I myself am not implemented, I shouldn't show my children, 
        # but I should show myself, so I can be switched back on
        if not component.implemented: 
            print 'No children from ',component
            return
        self.html+='<ul>\n'
        for c in children: self.__walk(c)
        self.html+='</ul>'
        
    def __debug(self):
        ''' Find the hanging chads, ie. the components that no longer have parents '''
        all=Component.objects.all()
        for a in all:
            found=(a.id in self.found)
            string='ok'
            if not found: 
                self.html+=self.__li(' class="bad"',a.id,a.abbrev,ok=1)+'</li>'
                p=Component.objects.filter(components=a.id)
                string=str(p)
            #print '%s(%s) shown in menu: %s (%s)(%s)'%(a.abbrev,a.id,found,a.scienceType,string)
            
            
       
class gridyuiTree2:
    ''' Provides an ordered list view of the grid heirarchy, for use
    by a yuiTree to control grid visibility '''
    def __li(self,e,i,a,ok=0):
        url=self.baseURL.replace(self.template,'%s'%i)
        ok1,ok2={0:('',''),1:('[',']')}[ok] #used to denote hanging chads (see debug)
        cc={1:' class="open"',0:''}[i==self.family.me]
        return '<li%s>%s<a href="%s"%s>%s</a>%s\n'%(e,ok1,url,cc,a,ok2)
    
    def __init__(self,grid_id,baseURL,top='topGrid',template='+EDID+'):
        grid=Grid.objects.get(pk=grid_id)
        self.baseURL=baseURL
        self.template=template
        self.html='<ul>\n'
        self.found=[]
        self.family=GridFamily(grid)
        self.expanders=self.family.ancestors
        self.expanders.append(self.family.me)
        #clist=Component.objects.filter(scienceType='model').filter(centre=component.centre_id)
        clist=Grid.objects.filter(istopGrid=True).filter(topGrid=grid.topGrid).order_by('id') 
        for c in clist: self.__walk(c)
        #self.__debug()
        self.html+='</ul>\n'
    
    def __walk(self,grid):
        ''' Show me and my children'''
        children=grid.grids.all().order_by('id')
        # we don't .order_by('abbrev') because we want the order we loaded them in ...
        classes=[]
        if grid.id in self.expanders: classes.append('expanded')
        if grid.id == self.family.me: classes.append('highlight') 
        cstring=''
        for i in classes:cstring+='%s '%i
        if cstring<>'': cstring=' class="%s"'%cstring[0:-1]
        self.html+=self.__li(cstring,grid.id,grid.abbrev)
        self.found.append(grid.id)
        if len(children)==0: return
        # now, if I myself am not implemented, I shouldn't show my children, 
        # but I should show myself, so I can be switched back on
        self.html+='<ul>\n'
        for c in children: self.__walk(c)
        self.html+='</ul>'
        
    def __debug(self):
        ''' Find the hanging chads, ie. the components that no longer have parents '''
        all=Grid.objects.all()
        for a in all:
            found=(a.id in self.found)
            string='ok'
            if not found: 
                self.html+=self.__li(' class="bad"',a.id,a.abbrev,ok=1)+'</li>'
                p=Grid.objects.filter(grids=a.id)
                string=str(p)
            #print '%s(%s) shown in menu: %s (%s)(%s)'%(a.abbrev,a.id,found,a.scienceType,string)
    
    