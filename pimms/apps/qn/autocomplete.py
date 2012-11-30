# django jquery autocomplete widget based on the django snippet http://www.djangosnippets.org/snippets/1097/
# json variant informed from http://solutions.treypiepmeier.com/2009/12/10/using-jquery-autocomplete-with-django/

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode 
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList, ValidationError
from django.conf import settings


logging=settings.LOG

# See http://docs.jquery.com/Plugins/Autocomplete/autocomplete#url_or_dataoptions for autocomplete options
CLIENT_CODEJS = """
<input type="text" name="%s_text" id="%s_text" %s value="%s" />
<input type="hidden" name="%s" id="%s" value="%s" />
<script type="text/javascript">
 $(function() {
        $('#%s_text').autocomplete('%s', {
            dataType: 'json',
            minchars: 3,
            max: 500,
            cacheLength: 40,
            selectFirst: false,
            parse: function(data) {
                return $.map(data, function(row) {
                    return { data:row, value:row[1], result:row[0] };
                });
            }
            }).result(
                function(e, data, value) {
                    $("#%s").val(value);
                }
            );
        }
    );
</script>
"""
class TermAutocompleteField(forms.fields.CharField):
    """
    Autocomplete form field for Model Model
    """
    model = None
    url = None
    
    def __init__(self, Vocab, vocabname, Term, size=0, *args, **kwargs):
       
        #self.url=reverse('pimms.apps.qn.views.completionHelper',args=(vocabname,))
        #self.url=reverse('ajax_value',args=(vocabname,))
        #FIXME: I can't work out how to make the above work without circular imports.
        self.url='/ajax/vocabs/%s'%vocabname
        self.vocab=Term.objects.filter(vocab=Vocab.objects.get(name=vocabname))
        
        super(TermAutocompleteField, self).__init__(
            widget = AutocompleteWidget(self.vocab,lookup_url=self.url,size=size),
            max_length=255,
            *args, **kwargs)

    def clean(self, value):
        if value==u'':
            # This is the case where nothing has been set anyway. 
            return None 
        # so this next is just a hack, but ...
        text=self.widget.submitted_text
        if text==u'': 
            #override the id returned, and assume the user wanted to set it to zero
            return None
        try: 
            obj = self.vocab.get(pk=value)
        except Exception,e:
            raise Exception,e
            #raise ValidationError(u'Invalid item selected')            
        return obj

class AutocompleteWidget(forms.widgets.TextInput):
    """ widget autocomplete for text fields
    """
    html_id = ''
    def __init__(self,vocab,
                 lookup_url=None, size=0,
                 *args, **kw):
        self.changed=False
        super(forms.widgets.TextInput, self).__init__(*args, **kw)
        # url for Datasource
        self.lookup_url = lookup_url
        self.vocab=vocab
        self.size=size
        
       
    def _has_changed(self, initial, data):
        if not self.changed:
            self.changed=forms.widgets.TextInput._has_changed(self,initial,data)
        return self.changed
        
    def render(self, name, value, attrs):
        if value == None:
            value = ''
        html_id = attrs.get('id', name)
        self.html_id = html_id
        #logging.debug('render value [%s] attributes %s'%(value,attrs))
        if value:
            vv=self.vocab.get(id=value)
        else: vv=''

        lookup_url = self.lookup_url
        
        if self.size<>0:
            sizestr='size="%s"'%self.size
        else: sizestr=''
       
        return mark_safe(CLIENT_CODEJS % (name, html_id, sizestr, vv, name, html_id, value, html_id,
                                       lookup_url,  html_id))


    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        value=data.get(name,None)
        
        # we need this to get a handle on contradictions
        text=data.get('%s_text'%name,None)
        self.submitted_text=text
        if value<>u'' and text==u'':
            # user is trying not to set this field
            self.changed=True
        
        return value