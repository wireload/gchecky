from xml.marshal import generic

# The original xml.marshal.generic does not know how to handle unicode strings.
# The code snippet below is taken from the python cookbook:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496923

class UnicodeMarshaller(generic.Marshaller):
    """
    Extends python marshal class with marshalling of the following value types:
     - bool into <true/> or <false/>
     - unicode into <unicode>...</unicode>
    TODO: more to come?
    """

    tag_unicode = 'unicode'

    def m_unicode(self, value, dict):
        name = self.tag_unicode
        L = ['<' + name + '>']
        s = value.encode('utf-8')
        if '&' in s:
            s = s.replace('&', '&amp;')
        if '<' in s:
            s = s.replace('<', '&lt;')
        if '>' in s:
            s = s.replace('>', '&gt;')
        L.append(s)
        L.append('</' + name + '>')
        return L

    def m_bool(self, value, dict):
        if value:
            return ['<true/>']
        return ['<false/>']

class UnicodeUnmarshaller(generic.Unmarshaller):
    def __init__(self):
        self.unmarshal_meth['unicode'] = ('um_start_unicode','um_end_unicode')
        self.unmarshal_meth['true'] = ('um_start_true','um_end_true')
        self.unmarshal_meth['false'] = ('um_start_false','um_end_false')
        # super maps the method names to methods
        generic.Unmarshaller.__init__(self)

    um_start_unicode = generic.Unmarshaller.um_start_generic
    um_start_true = generic.Unmarshaller.um_start_generic
    um_start_false = generic.Unmarshaller.um_start_generic

    def um_end_unicode(self, name):
        ds = self.data_stack
        # the value is a utf-8 encoded unicode
        ds[-1] = ''.join(ds[-1])
        self.accumulating_chars = 0

    def um_end_true(self, name):
        ds[-1] = true
        self.accumulating_chars = 0
    def um_end_false(self, name):
        ds[-1] = false
        self.accumulating_chars = 0
