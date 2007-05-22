
GOOGLE_CHECKOUT_SCHEMA = 'http://checkout.google.com/schema/2'

class Field(object):
    """Holds all the meta-information about mapping the current field value into/from
    the xml DOM tree.
    
    An instance of the class specifies the exact path to the DOM
    node/subnode/attribute that contains the field value. It also holds other
    field traits such as:
      @ivar required: required or optional
      @ivar empty: weither the field value could be empty (an empty XML tag)
      @ivar values: the list of acceptable values
      @ivar default: the default value for the field
      @ivar path: the path to the xml DOM node/attribute to store the field data
    """
    path     = ''
    required = True
    empty    = False
    default  = None
    values   = None

    @classmethod
    def deconstruct_path(cls, path):
        """Deconstruct a path string into pieces suitable for xml DOM processing.
            @param path: a string in the form of /chunk1/chunk2/.../chunk_n/@attribute.
                It denotes a DOM node or an attibute which holds this fields value.
                This corresponds to an hierarchy of type::
                  chunk1
                   \- chunk2
                      ...
                       \- chunk_n
                           \- @attribute
                Where chunk_n are DOM nodes and @attribute is a DOM attribute.
        
                Chunks and @attribute are optional.
                
                An empty string denotes the current DOM node.
            @return: C{(chunks, attribute)} - a list of chunks and attribute
            value (or None).
            @see: L{reconstruct_path}"""
        chunks = [chunk for chunk in path.split('/') if len(chunk)]
        attribute = None
        if chunks and chunks[-1][:1] == '@':
            attribute = chunks.pop()[1:]
        import re
        xml_name = re.compile(r'^[a-zA-Z\_][a-zA-Z0-9\-\_]*$') # to be fixed
        assert attribute is None or xml_name.match(attribute)
        assert 0 == len([True for chunk in chunks
                         if xml_name.match(chunk) is None])
        return chunks, attribute

    @classmethod
    def reconstruct_path(cls, chunks, attribute):
        """Reconstruct the path back into the original form using the deconstructed form.
           A class method.

            @param chunks: a list of DOM sub-nodes.
            @param attribute: a DOM attribute.
            @return: a string path denoting the DOM node/attribute which should contain
                the field value.
            @see: L{deconstruct_path}"""
        return '%s%s%s' % ('/'.join(chunks),
                           attribute and '@' or '',
                           attribute or '')

    def __init__(self, path, **kwargs):
        """Specify initial parameters for this field instance. The list of
        actual parameters depends on the subclass.
        @param path: The path determines the DOM node/attribute to be used
        to store/retrieve the field data value. It will be directly passed to
        L{deconstruct_path}."""
        for pname, pvalue in kwargs.items():
            setattr(self, pname, pvalue)
        if path is None:
            raise Exception('Path is a required parameter')
        self.path = path
        self.path_nodes, self.path_attribute = Field.deconstruct_path(path)


    def save(self, node, data):
        """Save the field data value into the DOM node. The value is stored
        accordingly to the field path which could be the DOM node itself or
        its subnodes (which will be automatically created), or (a sub)node
        attribute.
        @param node: The DOM node which (or subnodes of which) will contain
            the field data value.
        @param data: The data value for the field to be stored.
        """
        str = self.data2str(data)
        if self.path_attribute is not None:
            node.setAttribute(self.path_attribute, str)
        else:
            node.appendChild(node.ownerDocument.createTextNode(str))

    def load(self, node):
        """Load the field data from the xml DOM node. The value is retrieved
        accordingly to the field path and  other traits.
          @param node: The xml NODE that (or subnodes or attribute of which)
          contains the field data value.
          @see L{save}, L{__init__}"""
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
        """By default any data is valid"""
        return True

    def data2str(self, data):
        """Override this method in subclasses"""
        raise Exception('Abstract method of %s' % self.__class__)

    def str2data(self, str):
        """Override this method in subclasses"""
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

    def _traits(self):
        """Return the string representing the field traits.
        @see: L{__repr__}"""
        str = ':PATH(%s)' % (Field.reconstruct_path(self.path_nodes,
                                                    self.path_attribute),)
        str += ':%s' % (self.required and 'REQ' or 'OPT',)
        if self.empty:
            str += ':EMPTY'
        if self.default:
            str += ':DEF(%s)' % (self.default,)
        if self.values:
            str += ':VALS("%s")' % ('","'.join(self.values),)
        return str
    def __repr__(self):
        """Used in documentation. This method is called from subclasses
        __repr__ method to generate a human-readable description of the current
        field instance.
        """
        return '%s%s' % (self.__class__.__name__,
                         self._traits())

class NodeManager(type):
    """The class keeps track of all the subclasses of C{Node} class.
    
    It retrieves a C{Node} fields and provides this information to the class.
    
    This class represents a hook on-Node-subclass-creation where 'creation'
    means the moment the class is first loaded. It allows dynamically do some
    stuff on class load. It could also be done statically but that way we avoid
    code and effort duplication, which is quite nice. :-)
    
    @cvar nodes: The dictionary C{class_name S{rarr} class} keeps all the Node
    subclasses.
    """
    nodes = {}
    def __new__(cls, name, bases, attrs):
        """Dynamically do some stuff on a Node subclass 'creation'.
        
        Specifically do the following:
          - create the class (via the standard L{type.__new__})
          - retrieve all the fields of the class (its own and inherited)
          - store the class reference in the L{nodes} dictionary
          - give the class itself the access to its field list
        """
        clazz = type.__new__(cls, name, bases, attrs)
        NodeManager.nodes[name] = clazz
        fields = {}
        for base in bases:
            if hasattr(base, 'fields'):
                fields.update(base.fields())
        for fname, field in attrs.items():
            if isinstance(field, Field):
                fields[fname] = field
        clazz.set_fields(fields)
        return clazz

class Node(object):
    """The base class for any class which represents data that could be mapped
    into XML DOM structure.
    
    This class provides some basic functionality and lets programmer avoid
    repetetive tasks by automating it.
    
    @cvar _fields: list of meta-Fields of this class.
    @see: NodeManager
    """
    __metaclass__ = NodeManager
    _fields = {}
    @classmethod
    def set_fields(cls, fields):
        """Method is called by L{NodeManager} to specify this class L{Field}s
        set."""
        cls._fields = fields

    @classmethod
    def fields(cls):
        """Return all fields of this class (and its bases)"""
        return cls._fields

    def __new__(cls, **kwargs):
        """Creates a new instance of the class and initializes fields to
        suitable values. Note that for every meta-C{Field} found in the class
        itself, the instance will have a field initialized to the default value
        specified in the meta-L{Field}, or one of the L{Field} allowed values,
        or C{None}."""
        instance = object.__new__(cls)
        for fname, field in cls.fields().items():
            setattr(instance, fname, field.default)
            if field.default is None and field.values:
                setattr(instance, fname, field.values[0])
        return instance

    def __init__(self, **kwargs):
        """Directly initialize the instance with
        values::
          price = price_t(value = 10, currency = 'USD')
        is equivalent to (and preferred over)::
          price = price_t()
          price.value = 10
          price.currency = 'USD'
        """
        for name, value in kwargs.items():
            setattr(self, name, value)

    def write(self, node):
        """Store the L{Node} into an xml DOM node."""
        for fname, field in self.fields().items():
            data = getattr(self, fname, None)
            if data is None:
                if field.required: raise Exception('Field <%s> is required, but data for it is None' % (fname,))
                continue
            if (data != '' or not field.empty) and not field.validate(data):
                raise Exception('Invalid data for <%s> in %s' % (fname, data)) 
            field.save(field.set_path_node(node), data)

    def read(self, node):
        """Load a L{Node} from an xml DOM node."""
        for fname, field in self.fields().items():
            fnode = field.if_path_node(node)

            data = fnode and field.load(fnode)

            if data is None:
                if field.required:
                    raise Exception('Field <%s> is required, but data for it is None' % (fname,))
            elif data == '':
                if field.required and not field.empty:
                    raise Exception('Field <%s> can not be empty, but data for it is ""' % (fname,))
            else:
                if not field.validate(data):
                    raise Exception('Invalid data for <%s>: %s' % (fname, data))
            setattr(self, fname, data)

class DocumentManager(NodeManager):
    """Kepps track of all the L{Document} subclasses. Similar to L{NodeManager}
    automates tasks needed to be donefor every L{Document} subclass.

    The main purpose is to keep the list of all the classes and theirs
    correspongin xml tag names so that when an XML message is recieved it could
    be possible automatically determine the right L{Document} subclass
    the message corresponds to (and parse the message using the found
    document-class).

    @cvar documents: The dictionary of all the documents."""
    documents = {}

    def __new__(cls, name, bases, attrs):
        """Do some stuff for every created Document subclass.""" 
        clazz = NodeManager.__new__(cls, name, bases, attrs)
        DocumentManager.register_class(clazz, clazz.tag_name)
        return clazz

    @classmethod
    def register_class(self, clazz, tag_name):
        """Register the L{Document} subclass."""
        if tag_name is None:
            raise Exception('Document %s has to have tag_name attribute' % (clazz,))
        self.documents[tag_name] = clazz

    @classmethod
    def get_class(self, tag_name):
        """@return: the class by its xml tag name or raises an exception if
        no class was found for the tag name."""
        if not DocumentManager.documents.has_key(tag_name):
            raise Exception('There are no Document with tag_name(%s)' % (tag_name,))
        return self.documents[tag_name]

class Document(Node):
    """A L{Node} which could be stored as a standalone xml document.
    Every L{Document} subclass has its own xml tag_name so that it could be
    automatically stored into/loaded from an XML document.

    @ivar tag_name: The document's unique xml tag name."""
    __metaclass__ = DocumentManager
    tag_name = 'unknown'

    def toxml(self):
        """@return: A string for the XML document representing the Document
        instance."""
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
        """Read the text (as an XML document) into a Document (or subclass)
        instance.
        @return: A fresh-new instance of a Document (of the right subclas
        determined by the xml document tag name)."""
        from xml.dom.ext.reader import Sax2
        reader = Sax2.Reader()
        doc = reader.fromString(text)
        root = doc.documentElement
        clazz = DocumentManager.get_class(root.tagName)
        instance = clazz()
        instance.read(root)
        return instance

class List(Field):
    """The field describes a homogene list of values which could be stored
    as a set of XML nodes with the same tag names.
    
    An example - list of strings which should be stored as
    <messages> <message />* </messages>?::
      class ...:
          ...
          messages = gxml.List('/messages', gxml.String('/message'), required=False)

    @cvar list_item: a L{Field} instance describing this list items."""
    list_item = None

    # TODO required => default=[]
    def __init__(self, path, list_item, **kwargs):
        """Initializes the List instance.
        @param path: L{Field.path}
        @param list_item: a meta-L{Field} instance describing the list items
        """ 
        Field.__init__(self, path, **kwargs)
        if self.path_attribute is not None:
            raise Exception('List type %s cannot be written into an attribute %s' % (self.__class__, self.path_attribute))
        if list_item is None or not isinstance(list_item, Field):
            raise Exception('List item (%s) has to be a Field instance' % (list_item,))
        self.list_item = list_item

    def validate(self, data):
        """Checks that the data is a valid sequence."""
        from operator import isSequenceType
        if not isSequenceType(data):
            raise Exception('List data has to be a sequence (%s)' % (data,))
        return True

    def save(self, node, data):
        """Store the data list in a DOM node.
        @param node: the xml DOM node to hold the list
        @param data: a list of items to be stored"""
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
        """Load the list from the xml DOM node.
        @param node: the xml DOM node containing the list.
        @return: a list of items."""
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

    def __repr__(self):
        """Override L{Field.__repr__} for documentation purposes"""
        return 'List%s:[\n    %s\n]' % (self._traits(),
                                        self.list_item.__repr__())

class Complex(Field):
    """Represents a field which is not a simple POD but a complex data
    structure.
    An example - a price in USD::
        price = gxml.Complex('/unit-price', gxml.price_t)
    @cvar clazz: The class meta-L{Field} instance describing this field data.
    """
    clazz = None

    def __init__(self, path, clazz, **kwargs):
        """Initialize the Complex instance.
        @param path: L{Field.path}
        @param clazz: a Node subclass descibing the field data values."""
        if not issubclass(clazz, Node):
            raise Exception('Complex type %s has to inherit from Node' % (clazz,)) 
        Field.__init__(self, path, clazz=clazz, **kwargs)
        if self.path_attribute is not None:
            raise Exception('Complex type %s cannot be written into an attribute %s' % (self.__class__, self.path_attribute))

    def validate(self, data):
        """Checks if the data is an instance of the L{clazz}."""
        if not isinstance(data, self.clazz):
            raise Exception('Data(%s) is not of class %s' % (data, self.clazz))
        return True

    def save(self, node, data):
        """Store the data as a complex structure."""
        data.write(node)

    def load(self, node):
        """Load the complex data from an xml DOM node."""
        instance = self.clazz()
        instance.read(node)
        return instance

    def __repr__(self):
        """Override L{Field.__repr__} for documentation purposes."""
        return 'Node%s:{ %s }' % (self._traits(), self.clazz.__name__)

class String(Field):
    """Any text value."""
    def data2str(self, data):
        return '%s' % (data,)
    def str2data(self, text):
        return text

class Pattern(String):
    """A string matching a pattern.
    @ivar pattern: a regular expression to which a value has to confirm."""
    pattern = None
    def __init__(self, path, pattern, **kwargs):
        """Initizlizes a Pattern field.
        @param path: L{Field.path}
        @param pattern: a regular expression describing the format of the data"""
        String.__init__(self, path, pattern=pattern, **kwargs)

    def validate(self, data):
        """Checks if the pattern matches the data."""
        return not self.pattern.match(data) is None

class Decimal(Field):
    default=0
    def data2str(self, data):
        return '%d' % data
    def str2data(self, text):
        return int(text)

class Double(Field):
    """Floating point value"""
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
        pattern = re.compile(r'^[a-zA-Z0-9\.\_\%\-\+]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
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

