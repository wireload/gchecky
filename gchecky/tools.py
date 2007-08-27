from xml.marshal import generic

# The original xml.marshal.generic does not know how to handle unicode strings.
# The code snippet below is taken from the python cookbook:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496923

class UnicodeMarshaller(generic.Marshaller):
    tag_unicode = 'unicode'

    def m_unicode(self, value, dict):
        name = self.tag_unicode
        L = ['<' + name + '>']
        s = value.encode('utf-8')
        if '&' in s or '>' in s or '<' in s:
            s = s.replace('&', '&amp;')
            s = s.replace('<', '&lt;')
            s = s.replace('>', '&gt;')
        L.append(s)
        L.append('</' + name + '>')
        return L


class UnicodeUnmarshaller(generic.Unmarshaller):
    def __init__(self):
        self.unmarshal_meth['unicode'] = ('um_start_unicode','um_end_unicode')
        # super maps the method names to methods
        generic.Unmarshaller.__init__(self)

    um_start_unicode = generic.Unmarshaller.um_start_generic

    def um_end_unicode(self, name):
        ds = self.data_stack
        # the value is a utf-8 encoded unicode
        ds[-1] = ''.join(ds[-1])
        self.accumulating_chars = 0
