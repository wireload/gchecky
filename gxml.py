class Field(object):
    path     = ''
    default  = None
    required = True
    empty    = False
    values   = None

    @classmethod
    def deconstruct_path(cls, path):
        if path == '':
            return [], None
        chunks = path.split('/')
        attribute = None
        last = chunks[-1]
        if last.startswith('@'):
            attribute = chunks.pop()[1:]
        return chunks, attribute

    def __init__(self, path, **kwargs):
        for pname, pvalue in kwargs.items():
            setattr(self, pname, pvalue)
        if path is None:
            raise Exception('Path is a required parameter')
        self.path = path
        self.path_nodes, self.path_attribute = Field.deconstruct_path(path)

    def save(self, node, data):
        str = self.data2str(data)
        if self.path_attribute is not None:
            node.setAttribute(self.path_attribute, str)
        else:
            node.appendChild(node.ownerDocument.createTextNode(str))
    def load(self, node):
        from xml.dom.Document import Node as XmlNode
        if self.path_attribute is not None:
            if not node.hasAttribute(self.path_attribute):
                return None
            str = node.getAttribute(self.path_attribute)
        else:
            if node.nodeType == XmlNode.TEXT_NODE or node.nodeType == XmlNode.CDATA_SECTION_NODE:
                str = node.data
            else:
                str = ''.join([el.data for el in node.childNodes
                               if (el.nodeType == XmlNode.TEXT_NODE
                                   or el.nodeType == XmlNode.CDATA_SECTION_NODE)])
        return self.str2data(str)

    def validate(self, data):
        return True
    def data2str(self, data):
        raise Exception('Abstract method of %s' % self.__class__)
    def str2data(self, str):
        raise Exception('Abstract method of %s' % self.__class__)

    def set_path_node(self, parent):
        for nname in self.path_nodes:
            node = parent.ownerDocument.createElement(nname)
            parent.appendChild(node)
            parent = node
        return parent

    def get_path_nodes(self, parent):
        from xml.dom.Document import Node as XmlNode
        elements = [parent]
        for nname in self.path_nodes:
            els = []
            for el in elements:
                children = el.childNodes
                for i in range(0, children.length):
                    item = children.item(i)
                    if item.nodeType == XmlNode.ELEMENT_NODE:
                        if item.tagName == nname:
                            els.append(item)
            elements = els
        return elements
    def get_path_node(self, parent):
        els = self.get_path_nodes(parent)
        if len(els) != 1:
            raise Exception('Multiple nodes where exactly one is expected %s' % (self.path_nodes,))
        return els[0]
    def if_path_node(self, parent):
        els = self.get_path_nodes(parent)
        if len(els) > 1:
            raise Exception('Multiple nodes where at most one is expected %s' % (self.path_nodes,))
        if len(els) == 0:
            return None
        return els[0]

class NodeManager(type):
    nodes = {}
    def __new__(cls, name, bases, attrs):
        clazz = type.__new__(cls, name, bases, attrs)
        NodeManager.nodes[name] = clazz
        fields = {}
        for fname, field in attrs.items():
            if isinstance(field, Field):
                fields[fname] = field
        clazz.set_fields(fields)
        return clazz

class Node(object):
    __metaclass__ = NodeManager
    _fields = {}
    @classmethod
    def set_fields(cls, fields):
        cls._fields = fields
    @classmethod
    def fields(cls):
        return cls._fields
    def __new__(cls, **kwargs):
        instance = object.__new__(cls)
        for fname, field in cls.fields().items():
            setattr(instance, fname, field.default)
            if field.default is None and not field.values is None:
                setattr(instance, fname, field.values[0])
        return instance
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
    def write(self, node):
        for fname, field in self.fields().items():
            data = getattr(self, fname, None)
            if data is None:
                if field.required: raise Exception('Field <%s> is required, but data for it is None' % (fname,))
                continue
            if not field.validate(data):
                raise Exception('Invalid data for <%s> in %s' % (fname, data)) 
            field.save(field.set_path_node(node), data)
    def read(self, node):
        for fname, field in self.fields().items():
            fnode = field.if_path_node(node)

            data = fnode and field.load(fnode)

            if data is None:
                if field.required:
                    raise Exception('Field <%s> is required, but data for it is None' % (fname,))
            else:
                if not field.validate(data):
                    raise Exception('Invalid data for <%s>: %s' % (fname, data)) 
            setattr(self, fname, data)

class DocumentManager(NodeManager):
    documents = {}
    def __new__(cls, name, bases, attrs):
        clazz = NodeManager.__new__(cls, name, bases, attrs)
        DocumentManager.register_class(clazz, clazz.tag_name)
        return clazz
    @classmethod
    def register_class(self, clazz, tag_name):
        if tag_name is None:
            raise Exception('Document %s has to have tag_name attribute' % (clazz,))
        self.documents[tag_name] = clazz
    @classmethod
    def get_class(self, tag_name):
        if not DocumentManager.documents.has_key(tag_name):
            raise Exception('There are no Document with tag_name(%s)' % (tag_name,))
        return self.documents[tag_name]

GOOGLE_CHECKOUT_SCHEMA = 'http://checkout.google.com/schema/2'
class Document(Node):
    __metaclass__ = DocumentManager
    tag_name = 'unknown'
    def toxml(self):
        from xml.dom import implementation
        namespace = GOOGLE_CHECKOUT_SCHEMA
        tag_name = self.__class__.tag_name
        dt = implementation.createDocumentType(tag_name, '', '')
        doc = implementation.createDocument(namespace, tag_name, dt)
        self.write(doc.documentElement)
        from xml.dom.ext import PrettyPrint
        import StringIO
        output = StringIO.StringIO()
        PrettyPrint(doc, stream=output)
        text = output.getvalue()
        output.close()
        return text
    @classmethod
    def fromxml(self, text):
        from xml.dom.ext.reader import Sax2
        reader = Sax2.Reader()
        doc = reader.fromString(text)
        root = doc.documentElement
        clazz = DocumentManager.get_class(root.tagName)
        instance = clazz()
        instance.read(root)
        return instance

class List(Field):
    list_item = None
    # TODO required => default=[]
    def __init__(self, path, list_item, **kwargs):
        Field.__init__(self, path, **kwargs)
        if self.path_attribute is not None:
            raise Exception('List type %s cannot be written into an attribute %s' % (self.__class__, self.path_attribute))
        if list_item is None or not isinstance(list_item, Field):
            raise Exception('List item (%s) has to be a Field instance' % (list_item,))
        self.list_item = list_item

    def validate(self, data):
        from operator import isSequenceType
        if not isSequenceType(data):
            raise Exception('List data has to be a sequence (%s)' % (data,))
        return True

    def save(self, node, data):
        # node = self.list_item.set_path_node(node)
        for item_data in data:
            if item_data is None:
                if self.list_item.required: raise Exception('Required data is None')
                continue
            if not self.list_item.validate(item_data):
                raise Exception('Invalid data! %s in %s' % (item_data, self.list_item))
            inode = self.list_item.set_path_node(node) 
            self.list_item.save(inode, item_data)

    def load(self, node):
        data = []
        for inode in self.list_item.get_path_nodes(node):
            if inode is None:
                if self.list_item.required: raise Exception('Required data is None')
                data.append(None)
            else:
                idata = self.list_item.load(inode)
                if not self.list_item.validate(idata):
                    raise Exception('Invalid data! %s in %s' % (idata, self.list_item)) 
                data.append(idata)
        return data

class Complex(Field):
    clazz = None
    def __init__(self, path, clazz, **kwargs):
        if not issubclass(clazz, Node):
            raise Exception('Complex type %s has to inherit from Node' % (clazz,)) 
        Field.__init__(self, path, clazz=clazz, **kwargs)
        if self.path_attribute is not None:
            raise Exception('Complex type %s cannot be written into an attribute %s' % (self.__class__, self.path_attribute))
    def validate(self, data):
        if not isinstance(data, self.clazz):
            raise Exception('Data(%s) is not of class %s' % (data, self.clazz))
        return True
    def save(self, node, data):
        data.write(node)
    def load(self, node):
        instance = self.clazz()
        instance.read(node)
        return instance

class String(Field):
    def data2str(self, data):
        return '%s' % data
    def str2data(self, text):
        return text

class Pattern(String):
    pattern = None
    def __init__(self, path, pattern, **kwargs):
        String.__init__(self, path, pattern=pattern, **kwargs)
    def validate(self, data):
        return not self.pattern.match(data) is None

class Decimal(Field):
    default=0
    def data2str(self, data):
        return '%d' % data
    def str2data(self, text):
        return int(text)

class Double(Field):
    def data2str(self, data):
        return '%f' % data
    def str2data(self, text):
        return float(text)

class Boolean(Field):
    values = (True, False)
    def data2str(self, data):
        return (data and 'true') or 'false'
    def str2data(self, text):
        if text == 'true':
            return True
        if text == 'false':
            return False
        return 'invalid'

class Long(Field):
    default=0
    def data2str(self, data):
        return '%d' % (data,)
    def str2data(self, text):
        return long(text)

class Integer(Long):
    pass

class Url(Pattern):
    def __init__(self, path, **kwargs):
        import re
        # The general syntax for URI is:
        # pattern = re.compile(r'^((ht|f)tp(s?)\:\/\/|~/|/)?([\w]+:\w+@)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?((/?\w+/)+|/?)(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?')
        pattern = re.compile(r'^(http(s?)\:\/\/|~/|/)?([\w]+:\w+@)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?((/?\w+/)+|/?)(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?$')
        Pattern.__init__(self, path, pattern=pattern, **kwargs)

class Email(Pattern):
    def __init__(self, path, **kwargs):
        import re
        pattern = re.compile(r'^[a-zA-Z0-9._%-\+]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        Pattern.__init__(self, path, pattern=pattern, **kwargs)

class Phone(Pattern):
    def __init__(self, path, **kwargs):
        import re
        pattern = re.compile(r'^[0-9\+\-\(\)\ ]+$')
        Pattern.__init__(self, path, pattern=pattern, **kwargs)

class Zip(Pattern):
    def __init__(self, path, complete=True, **kwargs):
        import re
        if complete:
            pattern = re.compile(r'^[0-9a-zA-Z]+$')
        else:
            pattern = re.compile(r'^[0-9a-zA-Z\*]+$')
        Pattern.__init__(self, path, pattern=pattern, **kwargs)

class IP(Pattern):
    def __init__(self, path, **kwargs):
        import re
        num_pattern = r'(([1-9][0-9]?)|(1[0-9]{2})|(2((5[0-5])|([0-4][0-9]))))'
        pattern = re.compile(r'^%s\.%s\.%s\.%s$' % (num_pattern,num_pattern,num_pattern,num_pattern))
        Pattern.__init__(self, path, pattern=pattern, **kwargs)

# TODO
class ID(String):
    empty = False
    def validate(self, data):
        return len(data) > 0

class Any(Field):
    # TODO
    def data2str(self, data):
        return 'Any'
    def str2data(self, text):
        return True

#class DateTime(Field):
#    from datetime import datetime
#    def validate(self, data):
#        return isinstance(data, datetime)
#    def data2str(self, data):
#        pass

class Timestamp(Field):
    def validate(self, data):
        from datetime import datetime
        return isinstance(data, datetime)
    def data2str(self, data):
        return data.isoformat()
    def str2data(self, text):
        from datetime import datetime
        from xml.utils import iso8601
        # 2007-04-23T14:31:54.000Z
        # d = (0, 0, 0)
        return datetime.fromtimestamp(iso8601.parse(text))

