#!/usr/bin/python

def check_sample_xml():
    import os, sys, os.path
    import gchecky.gxml, gchecky.model
    samples_path = os.path.dirname(__file__) + '/docs/.xml/SampleXML/'
    for (dirpath, dirnames, filenames) in os.walk(samples_path):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() == '.xml':
                xmlname = dirpath + filename
                try:
                    xml_text = ''.join(open(xmlname, 'r').readlines()) + '\n'
                    doc = gchecky.gxml.Document.fromxml(xml_text)
                except Exception, msg:
                    print '\n' + xmlname
                    print 'Error:\n   %s' % (msg,)

if __name__ == '__main__':
    import unittest
    runner = unittest.TextTestRunner()
    from gchecky.test import allTestSuite
    runner.run(allTestSuite())
    # Also test loading of the samples provided by google
    check_sample_xml()
