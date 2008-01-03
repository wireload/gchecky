from xml import dom
from xml.dom import implementation


if __name__ == '__main__':
    import unittest
    runner = unittest.TextTestRunner()
    from gchecky.test import allTestSuite
    runner.run(allTestSuite())
