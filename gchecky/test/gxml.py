import unittest

from gchecky import gxml

class XmlNodeTestCase(unittest.TestCase):
    def setUp(self):
        class A(gxml.Node):
            a = gxml.String('a', default='aa')
            b = gxml.String('b', required=False)
        self.A = A
        self.a = A()
        class B(A):
            c = gxml.String('c', required=True, values=('cc1', 'cc2'))
        self.B = B
        self.b = B()
    def testClassFields(self):
        assert (self.A.fields().keys() == ['a','b'])
    def testSubclassFields(self):
        fnames = self.B.fields().keys()
        fnames.sort()
        assert (fnames == ['a','b','c'])
    def testObjectValues(self):
        assert self.a.a == 'aa', 'Default value is not set to a field'
        assert self.a.b == None, 'None is not set to a non-required field'
    def testSubObjectValues(self):
        assert self.b.a == self.a.a and self.b.b == self.a.b, ''
        assert self.b.c == 'cc1', 'None is not set to a non-required field'

def xmlNodeSuite():
    suite = unittest.TestSuite()
    suite.addTest(XmlNodeTestCase('testClassFields'))
    suite.addTest(XmlNodeTestCase('testSubclassFields'))
    suite.addTest(XmlNodeTestCase('testObjectValues'))
    suite.addTest(XmlNodeTestCase('testSubObjectValues'))
    return suite

class XmlFieldTestCase(unittest.TestCase):
    def testDeconstructPath(self):
        """Test Field.deconstruct_path method"""
        assert gxml.Field.deconstruct_path('/') == ([], None)
        assert gxml.Field.deconstruct_path('//') == ([], None)
        assert gxml.Field.deconstruct_path('aa') == (['aa'], None)
        assert gxml.Field.deconstruct_path('/aa') == (['aa'], None)
        assert gxml.Field.deconstruct_path('aa/') == (['aa'], None)
        assert gxml.Field.deconstruct_path('/aa/') == (['aa'], None)
        assert gxml.Field.deconstruct_path('aa/bb/cc') == (['aa', 'bb', 'cc'], None)
        assert gxml.Field.deconstruct_path('a/b/c') == (['a', 'b', 'c'], None)
        assert gxml.Field.deconstruct_path('@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('@b') == ([], 'b')
        assert gxml.Field.deconstruct_path('/@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('//@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('aa/@bb') == (['aa'], 'bb')
        assert gxml.Field.deconstruct_path('/aa/@bb') == (['aa'], 'bb')
        assert gxml.Field.deconstruct_path('aa/bb/@cc') == (['aa', 'bb'], 'cc')

def xmlFieldSuite():
    suite = unittest.TestSuite()
    suite.addTest(XmlFieldTestCase('testDeconstructPath'))
    return suite

if __name__ == '__main__':
    unittest.main()


