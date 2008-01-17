"""
>>> def test_enc_dec(data):
...   from xml.dom.minidom import parseString
...   doc = parseString('<?xml version="1.0"?><dummy/>')
...   encoder().serialize(data, doc.documentElement)
...   xml = doc.toprettyxml('  ')
...   data2 = decoder().deserialize(doc.documentElement)
...   if data2 != data:
...       print '--- Expected: ---'
...       print data
...       print '--- Got: ---'
...       print data2
...       print '=== Xml: ==='
...       print xml
>>> test_enc_dec(None)
>>> test_enc_dec(True)
>>> test_enc_dec(False)
>>> test_enc_dec('string')
>>> test_enc_dec(u'string')
>>> test_enc_dec({'a':'b'})
>>> test_enc_dec([1,2])
>>> test_enc_dec(['1',2])
>>> test_enc_dec([1])
>>> test_enc_dec({'':'aa'})
"""

TRUE_LABEL = u'True'
FALSE_LABEL = u'False'

class decoder:
    """
#    >>> def test(xml):
#    ...   from xml.dom.minidom import parseString
#    ...   doc = parseString(xml)
#    ...   d = decoder()
#    ...   return d.deserialize(doc.documentElement)
#    >>> test('<?xml version="1.0"?><dummy>aaa</dummy>')
#    >>> test('<?xml version="1.0"?><dummy><_>aaa</_><_>5</_><_>1.6</_></dummy>')
    """
    def deserialize(self, node):
        data = self._decode_into_dict(node)
        return data

    def _reduce_diction(self, diction):
        if len(diction) == 0:
            return None
        if len(diction) == 1:
            if None in diction:
                assert len(diction[None]) == 1
                return diction[None][0]
            if '_' in diction:
                data = diction['_']
                if not isinstance(data, list):
                    data = [data]
                return data
        data = {}
        for key in diction.keys():
            if key is None:
                data[None] = diction[None]
            else:
                data[decoder._decode_tag(key)] = diction[key]
            # elif data '_'
        return data

    @classmethod
    def _decode_tag(clazz, tag):
        if len(tag) > 1 and tag[0:2] == '__':
            return tag[2:]
        return tag

    def _decode_into_dict(self, node):
        diction = {None:[]}
        for child in node.childNodes:
            if child.nodeType is child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
                diction[None].append(decoder._decode_string(child.data))
            elif node.nodeType is child.ELEMENT_NODE:
                data = self._decode_into_dict(child)
                self._add_to_dict(diction, child.tagName, data)
            else:
                #TODO !!
                pass
        for attr in node.attributes.keys():
            data = decoder._decode_string(node.attributes[attr])
            self._add_to_dict(diction, attr, data)
        if len(diction[None]) == 0:
            del diction[None]
        return self._reduce_diction(diction)

    def _add_to_dict(self, diction, key, data):
        if key not in diction:
            diction[key] = data
        else:
            if not isinstance(diction[key], list):
                diction[key] = [diction[key]]
            diction[key].append(data)

    @classmethod
    def _decode_string(clazz, str):
        """
        >>> decoder._decode_string(None)
        >>> decoder._decode_string('True')
        True
        >>> decoder._decode_string('False')
        False
        >>> decoder._decode_string('11')
        11
        >>> decoder._decode_string('12L')
        12L
        >>> decoder._decode_string('11.')
        11.0
        >>> decoder._decode_string('"some"')
        u'some'
        >>> decoder._decode_string('"some')
        u'"some'
        """
        if str is None:
            return None
        elif str == TRUE_LABEL:
            return True
        elif str == FALSE_LABEL:
            return False
        try:
            return int(str)
        except ValueError:pass
        try:
            return long(str)
        except ValueError:pass
        try:
            return float(str)
        except ValueError:pass
        str = unicode(str)
        if str[0] == '"' and str[-1] == '"':
            original = str[1:-1].replace('\\"', '"')
            if encoder._escape_string(original) == str:
                return original
        return unicode(str)

class encoder:
    """
#   >>> e = encoder()
#   >>> def test(data):
#   ...   from xml.dom.minidom import parseString
#   ...   doc = parseString('<?xml version="1.0"?><dummy/>')
#   ...   encoder().serialize(data, doc.documentElement)
#   ...   return doc.toprettyxml('  ')
#   ...
#   >>> test(True)
#   >>> test(False)
#   >>> test(15)
#   >>> test(16.)
#   >>> test(17.5612)
#   >>> test('something')
#   >>> test(u'unicode')
#   >>> test([1,2,3])
#   >>> test((1,2,3))
#   >>> test((1,))
#   >>> test({'a':'b'})
    """
    def serialize(self, data, xml_node):
        self.__doc = xml_node.ownerDocument
        self.__markers = {}
        self._encode(data=data, node=xml_node)

    @classmethod
    def _encode_tag(clazz, tag):
        return '__' + tag

    def _create_element(self, tag):
        # TODO Account for wierd characters
        return self.__doc.createElement(tag)

    def _create_text(self, value):
        return self.__doc.createTextNode(value)

    @classmethod
    def _escape_string(clazz, str):
        # TODO Do we have to escape '<', '>' and '&' ourselves?
        #      Or is this done by xml.dom.minidom?
        return '"' + str.replace('"', '\\"') + '"'

    def _encode(self, data, node):
        """
        @param node Is either a string or an XML node. If its a string then
                    a node with such a name should be created, otherwise
                    the existing xml node should be populated.
        """
        if isinstance(data, (list, tuple)):
            self.__mark(data)
            children = []
            if isinstance(node, basestring):
                tag = encoder._encode_tag(node)
                parent = None
            else:
                tag = '_'
                parent = node

            for d in data:
                child = self._create_element(tag)
                if parent is not None:
                    parent.appendChild(child)
                self._encode(d, child)
                children.append(child)

            return children
        else:
            if isinstance(node, basestring):
                parent = self._create_element(encoder._encode_tag(node))
            else:
                parent = node

            if isinstance(data, dict):
                self.__mark(data)

                for key in data.keys():
                    children = self._encode(data[key], key)
                    if isinstance(children, list):
                        for child in children:
                            parent.appendChild(child)
                    else:
                        parent.appendChild(children)
                self.__unmark(data)
            else:
                if isinstance(data, basestring):
                    child = self._create_text(encoder._escape_string(unicode(data)))
                elif data is None:
                    child = None
                elif isinstance(data, (int, long, float)):
                    child = self._create_text(unicode(data))
                elif data is True:
                    child = self._create_text(TRUE_LABEL)
                elif data is False:
                    child = self._create_text(FALSE_LABEL)
                else:
                    raise ValueError('Not supported.')
                if child is not None:
                    parent.appendChild(child)
            return [parent]

    def __mark(self, obj):
        if id(obj) in self.__markers:
            raise ValueError('gchecky.encoder can\'t handle cyclic references.')
        self.__markers[id(obj)] = obj

    def __unmark(self, obj):
        del self.__markers[id(obj)]

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

    def m_unicode(self, value, diction):
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

    def m_bool(self, value, diction):
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

if __name__ == "__main__":
    def run_doctests():
        import doctest
        doctest.testmod()
    run_doctests()
