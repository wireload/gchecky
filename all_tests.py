from xml import dom


if __name__ == '__main__':
    import unittest
    runner = unittest.TextTestRunner()
    from gchecky.test import allTestSuite
    runner.run(allTestSuite())
