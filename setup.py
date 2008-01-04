#!/usr/bin/python
from distutils.core import setup

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
from distutils.command.install import INSTALL_SCHEMES
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

version = __import__('gchecky').version()

setup(name='Gchecky',
      version=version,
      url='http://gchecky.googlecode.com',
      author='Evgeniy Tarassov',
      author_email='etarassov@gmail.com',
      description='Python wrapper for Google Checkout API Level 2',
      license='Apache License 2.0',
      packages=['gchecky', 'gchecky.test'],
      data_files=[],
      scripts=[],
)

